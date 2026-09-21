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
  receiver: default        # rota padrao, pega o que nao casar com nenhuma abaixo
  group_by: ['alertname', 'severity']

  routes:
  - matchers:
      - severity = "critical"
    receiver: email
    continue: true
  - matchers:
      - severity = "high"
    receiver: email
    continue: true

receivers:
  - name: default
  - name: email
    email_configs:
    - to: 'oncall@yourorganization.com'
      from: 'alertmanager@yourorganization.com'
      smarthost: smtp.gmail.com:587
      auth_username: 'alertmanager@yourorganization.com'
      auth_identity: 'alertmanager@yourorganization.com'
      auth_password: 'password'
```

Duas coisas importantes aqui.

A primeira é o `matchers`. Você vai encontrar muito tutorial (inclusive versões antigas deste curso) usando `match:` e `match_re:`. Eles estão **deprecated desde o Alertmanager 0.22** e podem sumir. A sintaxe nova é `matchers:`, com a comparação escrita numa linha só: `severity = "critical"`, `severity =~ "critical|high"`, `env != "dev"`.

A segunda é que `receivers` fica no topo do arquivo, no mesmo nível do `route` — não aninhado dentro dele. Todo receiver citado em alguma rota precisa existir nessa lista, inclusive o padrão.

Se for usar Gmail mesmo, o `auth_password` não é a senha da sua conta: o Google exige uma [senha de app](https://support.google.com/accounts/answer/185833). E valide o arquivo antes de aplicar, com `amtool check-config /etc/alertmanager/alertmanager.yml`.

Com isso a tua noite de sono agradece. =D
