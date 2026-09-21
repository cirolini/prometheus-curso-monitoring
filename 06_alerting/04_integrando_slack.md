# Notificações pelo Slack

Da mesma forma como receber notificações por email pode ajudar, enviar as notificações para o slack quando a tua empresa ja esta acostumada a trabalhar com ele pode ser de muita ajuda.

Primeiro você precisa de uma URL de webhook do Slack. O caminho mudou: hoje se cria um app em [api.slack.com/apps](https://api.slack.com/apps) → *Create New App* → *From scratch*, e dentro dele você ativa **Incoming Webhooks** e clica em *Add New Webhook to Workspace*, escolhendo o canal. Você vai precisar de permissão para instalar apps no workspace.

No fim você recebe uma URL no formato `https://hooks.slack.com/services/T000/B000/xxxx`. Guarde ela como segredo — quem tiver essa URL consegue postar no seu canal.

```
global:
  resolve_timeout: 5m
  # API URL to use for Slack
  slack_api_url: 'https://hooks.slack.com/services/XXX/XXX/XXXXXXXXX'
  # Se voce tem um receiver de email no arquivo, o smarthost precisa estar
  # aqui no global (ou dentro de cada email_configs). Sem isso o Alertmanager
  # nem sobe: o amtool acusa "no global SMTP smarthost set".
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alertmanager@yourorganization.com'

route:
  receiver: slack # Fallback

  routes:
  - matchers:
      - severity = "critical"
    receiver: slack
    continue: true
  - matchers:
      - severity = "high"
    receiver: slack
    continue: true
  - matchers:
      - severity = "info"
    receiver: mail

receivers:
- name: mail
  email_configs:
  - to: 'oncall@yourorganization.com'

- name: slack
  slack_configs:
  - channel: '#monitoring'
    send_resolved: true
```

Com isso, cada alerta que casar com uma das rotas vira uma mensagem no canal `#monitoring`, e o `send_resolved: true` faz o Alertmanager avisar também quando o problema se resolve — o que costuma ser tão útil quanto o alerta em si.
