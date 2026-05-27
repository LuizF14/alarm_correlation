from pathlib import Path
import tempfile
import shutil
import multiprocessing
from multiprocessing import cpu_count
import traceback

from tqdm import tqdm
import polars as pl

from src.postprocess.enumerate_incidents import EnumerateIncidents
from src.pipelines.correlation_base import CorrelationBase
from src.repository.alarm_graph_repository import AlarmGraphRepository
from src.utils.node_summary import node_summary


def _evaluate_window(args):
    algorithm_class, w, batch_size, parquet_dir = args  # recebe o path via args

    partitions = [
        pl.read_parquet(f)
        for f in sorted(Path(parquet_dir).glob("*.parquet"))
    ]

    path = f"graph_{algorithm_class.__name__}_{w}"
    graph_repo = AlarmGraphRepository(path, batch_size=batch_size)

    try:
        algorithm_class.internal_process(partitions, graph_repo, threshold_minutes=w, verbose=False)
        EnumerateIncidents.enumerate_data(graph_repo, verbose=False)
        summary, metrics = node_summary(graph_repo)
        return w, (summary, metrics), None
    except Exception as e:
        return w, None, traceback.format_exc()
    finally:
        graph_repo.delete_db()
        graph_repo.close()


_TOTAL_BATCH_BUDGET = 20_000_000


class SlidingWindowSearch:
    @staticmethod
    def search(
        algorithm: CorrelationBase,
        data,
        window_widths: list,
        n_workers: int | None = None,
    ):
        partitions = algorithm.common_preprocess(data)

        parquet_dir = tempfile.mkdtemp(prefix="sliding_window_")
        try:
            for i, part in enumerate(partitions):
                part.write_parquet(f"{parquet_dir}/{i:04d}.parquet")

            workers = min(n_workers or cpu_count(), len(window_widths))
            batch_size = max(1, _TOTAL_BATCH_BUDGET // workers)
            args = [(algorithm, w, batch_size, parquet_dir) for w in window_widths]

            results = {}
            errors = {}

            ctx = multiprocessing.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                jobs = pool.imap_unordered(_evaluate_window, args)

                with tqdm(
                    total=len(window_widths),
                    desc=f"Avaliando janelas ({algorithm.__name__}) | workers={workers} | batch={batch_size:,}",
                ) as bar:
                    for w, result, error in jobs:
                        if error:
                            errors[w] = error
                            bar.write(f"[ERRO] janela={w}s:\n{error}")
                        else:
                            results[w] = result

                        bar.set_postfix({"última": f"{w}s", "erros": len(errors)})
                        bar.update(1)
        finally:
            shutil.rmtree(parquet_dir)

        if errors:
            raise RuntimeError(
                f"{len(errors)} janela(s) falharam: {list(errors.keys())}"
            )

        return results