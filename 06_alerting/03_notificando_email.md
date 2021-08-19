# Sendo notificado por email

Nem sempre você vai estar olhando as interfaces do Alertmanager ou do Prometheus para poder ficar analisando os alertas, e fora desses horário pode querer ser notificado. O Alertmanager tem varias integrações com diversos sistemas de notificação, entre os mais famosos como Pager Duty, OpsGenie, Slack mas também por email.

É muito simples fazer a configuração para ele enviar email.

```
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'email'
receivers:
  - name: 'email'
    email_configs:
    - to: 'oncall@yourorganization.com'
      from: 'alertmanager@yourorganization.com'
      smarthost: smtp.gmail.com:587
      auth_username: 'alertmanager@yourorganization.com'
      auth_identity: 'alertmanager@yourorganization.com'
      auth_password: 'password'
```

A partir dessa configuração o Alertmanager vai enviar um email para cada alerta que temos. O que pode acabar com o sono de cada um, uma pratica mais comum é enviar notificações somente de alertas mais críticos, podemos criar rotas mais especificas para somente um nível de criticidade baseada nos labels dos alertas envie a notificação.

```
route:
  receiver: web.hook #default route
  group_by: ['alertname', 'severity']

  routes:
  - match:
      severity: critical
    receiver: email
    continue: true
  - match:
      severity: high
    receiver: email
    continue: true
  receivers:
    - name: 'email'
  ...
```

Com isso a tua noite de sono agradece. =D
