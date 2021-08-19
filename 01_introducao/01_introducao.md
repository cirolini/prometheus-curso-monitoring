# Introdução

A forma de monitorar sistemas e infra estrutura vem sendo melhorada ao longo dos anos. A Responsabilidades e ferramentas que antes eram exclusivas dos times de Operações agora são compartilhada entre desenvolvedores, administradores de redes e até mesmo outras areas da empresa como a area comercial, suporte a clientes, entre outras.

O modelo de monitoração tradicional onde saber se um serviço esta UP ou Down, cadastrar manualmente servidores em um sistema de monitoração não se aplicam mais ao novos modelos de aplicações como aquelas baseadas em microserviços, aplicações distribuídas ou aplicações em cloud onde a dinâmica de funcionamento é tão rápida que um serviço pode existir apenas por poucos segundos, as vezes até menos.

A monitoração, também conhecida atualmente como observability, agora esta muito mais focada na experiencia do usuário e na qualidade de um serviço. Atualmente também existem os SLOs, ou objetivos de nível de serviço, ajudam a definir e monitorar os sintomas de uma aplicação e focam em sintomas como erros, lentidão e saturação.

O Prometheus é uma ferramenta de monitoração e alerta moderna, que surgiu na SoundCloud em 2012, muito parecido com o Borgmon (que é o sistema de monitoração do Google). O Prometheus é um time series database, que basicamente é uma estrutura de dados otimizada para armazenar e servir dados através de pares de tempo e valores associados. Uma forma de explicar isso é pensar em uma linha de tempo e ir colocando os novos valores de uma mesma métrica em pontos dessa linha. Se formos fazer uma comparação simples com um banco de dados relacional, imagine que você nunca sobrescreve um valor de uma determinada informação, sempre acrescenta um novo com o valor de data e hora respectivo da inserção.

Mas muito mais do que isso, o conjunto de ferramentas do Prometheus ainda contem uma ferramenta para criar e lidar com alertas, o alertmanager, ferramentas para extrair informações de aplicações e servidores, os exporters, ferramentas para enviar dados para o Prometheus, o pushgateway, ferramentas de service discovery para não ser mais necessário ficar cadastrando servidores e aplicações manualmente, e uma linguagem de consulta poderosa e muito flexível para poder extrair não só informações simples, mas poder ter insights sobre os dados.

Proximo passo vamos falar sobre a arquitetura do Prometheus para entender melhor como todas essas ferramentas se conectam.
