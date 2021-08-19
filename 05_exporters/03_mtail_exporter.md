# Mtail Exporter

Muitas vezes a aplicação não vai poder gerar métricas diretamente para o Prometheus, ou os desenvolvedores não tem tempo ou simplesmente ela é tão antiga que ninguém mais quer mexer nela, ou qualquer outro motivo. Nesse caso existe um exporter capaz de ler os logs da aplicação e através de expressão regulares gerar estatísticas/métricas para aquela aplicação.

Não se envergonhe com isso, muitas vezes é o único caminho. Não esqueça que o mtail é um projeto do Google, então todo mundo passa por seus problema. =D

## Instalação

Bom a instalação do mtail não difere em muito dos outros exporters.

```
mkdir mtail
cd mtail
wget https://github.com/google/mtail/releases/download/v3.0.0-rc44/mtail_3.0.0-rc44_Linux_x86_64.tar.gz
tar xvfz mtail*.tar.gz
./mtail
```
A saida depois da execução vai te explicar que é necessario um arquivo de configuração para poder executar ele. Mas ja vamos criar o que é necessario para deixar ele em execução. Criamos os usuarios e o que for necessario

```
sudo useradd --no-create-home --shell /bin/false mtail_exporter
sudo mv mtail /usr/local/bin

mkdir /etc/mtail
chown mtail_exporter:mtail_exporter /etc/mtail
```

Criando o arquivo do systemd.

```
sudo vim /etc/systemd/system/mtail_exporter.service

[Unit]
Description=Mtail Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=mtail_exporter
Group=mtail_exporter
Type=simple
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/usr/local/bin/mtail -progs /etc/mtail/rule.mtail -logs /var/log/syslog

[Install]
WantedBy=multi-user.target
```

Agora iniciamos o node_exporter e colocamos ele para iniciar junto com o Sistema Operacional. Ainda não vai funcionar pq não criamos o nosso arquivo de regras, mas vamos a ele em seguida.

```
sudo systemctl daemon-reload
sudo systemctl start mtail_exporter
sudo systemctl status mtail_exporter
sudo systemctl enable mtail_exporter
```


## Programing guide

Para fazer o mtail coletar as métricas nós precisamos instruir a ele através de um conjunto de regras e expressão regulares para poder remover as regras, existe muitos métodos e formas, aqui vamos explicar o mais simples e pode procurar o guia de referencia aqui: https://google.github.io/mtail/Programming-Guide.html


Vamos criar o arquivo de conf do mtail o mais simples possível para entendermos:

```
# simple line counter
counter syslog_lines_total

/$/ {
  syslog_lines_total++
}
```

Vamos falsificar uma linha nova no `/var/log/syslog` para ver os números incrementarem:

```
echo "Mar 22 12:42:58 vagrant-ubuntu-trusty-64 cirolini[123]: teste" >> /var/log/syslog

curl localhost:3903/metrics | grep syslog_

# HELP syslog_lines_total defined at rule.mtail:2:9-19
# TYPE syslog_lines_total counter
syslog_lines_total{prog="rule.mtail"} 488
```

O que fizemos aqui? Vamos começar pelo rules.mtail. Primeira coisa definimos a métrica lines_total como um counter, ou seja é um valor que só vai ser incrementado. A abaixo a expressão regular precisa ser colocada entre `//` o $ serve para identificar um final de linha, ou seja a cada final de linha vamos incrementar o valor lines_total em 1.

Quando requisitamos as métricas do mtail e adicionamos novas linhas no arquivo do syslog podemos ver que o numero incrementa conforme vamos acrescentando linhas.

Agora vamos para um exemplo um pouco mais complexo.

```
counter syslog_lines_total
counter syslog_lines by hostname, application

# The `syslog' decorator defines a procedure.  When a block of mtail code is
# "decorated", it is called before entering the block.  The block is entered
# when the keyword `next' is reached.
def syslog {
    /(?P<date>(?P<legacy_date>\w+\s+\d+\s+\d+:\d+:\d+)|(?P<rfc3339_date>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+[+-]\d{2}:\d{2}))/ +
        /\s+(?:\w+@)?(?P<hostname>[\w\.-]+)\s+(?P<application>[\w\.-]+)(?:\[(?P<pid>\d+)\])?:\s+(?P<message>.*)/ {
        # If the legacy_date regexp matched, try this format.
        len($legacy_date) > 0 {
            strptime($legacy_date, "Jan _2 15:04:05")
        }
        # If the RFC3339 style matched, parse it this way.
        len($rfc3339_date) > 0 {
            strptime($rfc3339_date, "2006-01-02T15:04:05-07:00")
        }
        # Call into the decorated block
        next
    }
}

@syslog {
  /$/ {
    syslog_lines_total++
    syslog_lines[$hostname][$application]++
  }
}
```

Agora criamos dois contadores um para o total de linha como fizemos antes, e outro para contabilizar o numero de linhas por hostname e aplicação conforme aparecem no log.

Criamos uma classe chamada syslog, e essa classe ja faz toda a extração de dados via expressão regular e coloca em variáveis (no mundo das expressão regulares conhecido como Named Capture Group) que poderemos utilizar mais tarde.

Depois ainda fazemos alguns testes de consistência no formato de data, e após isso usamos a nossa expressão função para extrair os valores que ja pré determinamos, mas ainda poderíamos usar outras expressão regulares para extrair informações diferentes e armazenar em outras variáveis.

Um bom lugar para brincar com as regex é: https://regex101.com/
