# Silenciando Alertas

Uma parte importante de todo sistema de monitoração é a habilidade de suprimir, nos termos do prometheus, silenciar alertas por um período de tempo. Isso é util em muitos modos, tanto para alertas que estão acontecendo e vão precisar de muito tempo para serem resolvidos, mas também para quando vamos entrar em alguma manutenção e queremos deixar uma plataforma inteira em manutenção.

Para silenciar os alertas podermos ir diretamente pela interface do Alertmanager, clicar em silences e podemos criar novos silences.

![Alertmanager-silence1](/06_alerting/images/alertmanager-silence1.png "Alertmanager-silence1")

![Alertmanager-silence2](/06_alerting/images/alertmanager-silence2.png "Alertmanager-silence2")

![Alertmanager-silence3](/06_alerting/images/alertmanager-silence3.png "Alertmanager-silence3")

Quando não quiser mais o silence ativo, pode clicar no botão de expirar. Ou simplismente esperar o tempo de silence que colocou para ele acabar.
