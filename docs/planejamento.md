# Planejamento do projeto

1. Primeiramente, será feita uma análise geral dos dados. Montarei vários gráficos para tentar descobrir quais vão nos ajudar melhor a visualizar o problema e resolvê-lo.
2. Fazer um clusterização e dimensionalização desses dados:
    2.1. Testar o DBSCAN, HDBSCAN
    2.2. Testar o k-means
    2.3. Testar Spectral Clustering
    2.4. Testar Gaussian Mixture
3. Transformar em grafos:
    3.1. Grafo de coocorrência temporal
    3.2. Grafo por similaridade (cosine-similarity, por exemplo)
    3.3. Grafo por correlação entre as séries temporais (Correlação de Pearson)
    3.4. Grafo de causalidade (Granger Causality, Dynamic Bayesian Networks, PCMCI)