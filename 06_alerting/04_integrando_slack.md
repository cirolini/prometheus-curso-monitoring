# Notificações pelo Slack

Da mesma forma como receber notificações por email pode ajudar, enviar as notificações para o slack quando a tua empresa ja esta acostumada a trabalhar com ele pode ser de muita ajuda.

Primeiro você precisa criar uma URL para a api do slack, para criar uma você precisa ser administrador do seu workspace e ir em Administration -> Manage apps.

Depois basta procurar por Incoming WebHooks e vai aparecer uma tela como essa:

![AlertmanagerWebHooks](https://grafana.com/static/assets/img/blog/AlertmanagerWebHooks.png "AlertmanagerWebHooks")

Logo após você vai ter uma tela com a Webhook URL e vamos configurar o Alertmanager para enviar as notificações.

```
global:
  resolve_timeout: 5m
  # API URL to use for Slack
  slack_api_url: 'https://hooks.slack.com/services/XXX/XXX/XXXXXXXXX'

route:
  receiver: slack # Fallback

  routes:
  - match:
      severity: critical
    receiver: slack
    continue: true
  - match:
      severity: high
    receiver: slack
    continue: true
  - match:
      severity: email
    receiver: mail

receivers:
- name: mail
  email_configs:
  - to: oncall@yourorganization.com'
  ...

- name: slack
  slack_configs:
  - channel: '#monitoring'
    send_resolved: true
```

As mensagens vão aparecer no slack como nas imagens abaixo:

![AlertmanagerSlack](/06_alerting/images/alertmanager_slack.png "AlertmanagerSlack")

![AlertmanagerSlack2](/06_alerting/images/alertmanager_slack2.png "AlertmanagerSlack2")
