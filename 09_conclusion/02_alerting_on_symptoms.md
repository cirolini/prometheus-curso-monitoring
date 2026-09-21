# Alertando sobre os sintomas

O que vou falar aqui é baseado na minha experiencia com alertas e também no brilhante artigo do Rob Ewaschuk https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/edit sobre uma filosofia sobre alertas.

# Alertas são problemas

Primeiro, alertas que requerem a atenção de um humano, muitas vezes conhecido como Pages, ou também aqueles alertas que vão acordar alguem de madrugada ou tirar a atenção de alguem durante o dia devem ser urgentes, importantes, passíveis de ação e reais. O problema de ter o over-monitoring ou mais alertas do que podemos controlar significa que os analistas responsáveis vão parar de dar atenção para os alertas, ignorar eles quando acontecerem.

Um resumo é que um alerta tem que representar um PROBLEMA, e esse problema deve ter uma ação relacionada a ele. As ações podem ser conduzir uma investigação, alguma ação como remover um servidor defeituoso do balanceamento, criar uma ação de bugfix, ou até mesmo disparar uma ação de capacity planning.

Alertas baseados em sintomas e não em causa raiz pode reduzir o "barulho", ou uma quantidade desnecessária de alertas. Basicamente temos que criar alertas baseados no que afeta o usuário. Por exemplo, um usuário não se importa se o microserviço esta reiniciando ele se importa se esta tendo erros 500 enquanto acessa o serviço. Ou um usuário não se importa se o banco de dados esta com alto consumo de CPU e sim se a aplicação esta mais lenta.

Mas em contrapartida muitas vezes o banco pode estar com uma CPU mais alta e isso não representar um problema, ou um microserviço estar sendo reiniciado mas isso não afeta os usuários. Então isso não deveria alertar, deveria ser algum indicador em dashboards ou outras métricas.

Claro que em outras vezes alertar na causa raiz é necessário, e pode ser usado para prevenir ou agilizar em um momento de troubleshooting. Por exemplo alarmar antes de um disco chegar no limite da capacidade para disparar alguma ação de capacity planning.

Importante que os alertas tenham playbooks ou runbooks, com informações sobre o que fazer, diagramas, informações sobre logs, dashboards etc. Gosto de falar que devemos desenvolver sistemas como se quando eles derem problema seremos acordados a noite, para isso não acontecer eles devem conter bons runbooks, com os problemas conhecidos e melhores praticas de troubleshooting.

Os alertas precisam ser rastreáveis e passíveis de ter relatórios. Usando a própria querylanguage do prometheus é possivel extrair bons resultados. Mas revisões constantes da quantidade de alertas, os alertas que mais são acionados, e o possível trabalho para diminuir os mesmos pode ajudar bastante a resolver problemas e diminuir o numero de incidentes.

A partir desses pontos conseguimos manter um sistema de observability mais confiável e preciso.
