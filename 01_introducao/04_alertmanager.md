Primeiro vamos entender um pouco do Alertmanager e para que ele serve. Os alertas no Prometheus são divididos em duas partes, as regras dos alertas são feitas no Prometheus que envia os sinais de alertas para o Alertmanager, que funciona para administrar esses alertas incluindo opções como silenciar os alertas, agrega-los ou enviar eles para algum outro sistema de notificação como email, slack, Pagerdutty ou similares.

Vamos aos principais conceitos do Alertmanager:

## Agrupamento

O Alertmanager tem regras para agrupar e categorizar certos tipos de alertas. Isso é especialmente util durante catástrofes, onde vc pode ter centenas, em alguns casos milhares de serviços que podem falhar com uma mesma causa raiz e alertar simultaneamente. Para a própria visualização do problema e compreensão do ocorrido é melhor que eles fiquem agrupados por tipo, plataforma ou outros, e enviem somente um sinal para o analista de plantão.

## Inibição

É a capacidade de não notificar um alerta caso algum outro alerta pré-definido esteja acontecendo.

Por exemplo, vários serviços são conectados a uma base de dados, quando a base de dados ficar totalmente offline, não é necessário ter alertas de todas as outras aplicações conectadas a ela e podemos simplesmente suprimi-los.

## Silenciar

Algumas vezes um alerta pode demandar horas ou dias de trabalho, e o Alertmanager tem a capacidade de silenciar um alerta para que não gere notificações, e também que novos alertas ja entrem silenciados. Uma manutenção pré programada também pode gerar um silence para que durante aquele período não tenham alertas.

## Alta disponibilidade

Em alguns casos você pode precisar de mais de um Alertmanager em diferentes servidores ou localidades para garantir que mesmo com a falha de uma instancia o Alertmanager continue funcionando.


Agora que entendemos o funcionamento básico do Prometheus e do Alertmanager vamos para a instalação de toda a plataforma.
