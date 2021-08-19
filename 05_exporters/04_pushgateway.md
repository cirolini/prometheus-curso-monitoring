# Pushgateway

Uma das premissas do prometheus é que ele coleta as métricas, ou seja ele busca de alguma forma as métricas na aplicação ou servidor que estamos buscando o que queremos saber. Mas o que fazer com jobs efêmeros, ou cron jobs que querem enviar a sua métrica para o prometheus antes que eles deixem de existir? Para isso existe o pushgateway que é uma forma de enviar dados para o Prometheus.

# Instalando

Agora vamos fazer um pouco diferente do que fizemos antes, podemos claro baixar o binário e instalar ele no nosso ubuntu, mas nesse caso, como em geral é recomendado ter o pushgateway em uma estrutura separada do prometheus vamos colocar ele em um container:

```
docker pull prom/pushgateway
docker run -d -p 9091:9091 prom/pushgateway
```

Depois disso precisamos enviar alguma métrica para o pushgateway, para isso vamos usar o curl:

```
echo "some_metric 3.322" | curl --data-binary @- http://localhost:9091/metrics/job/some_job
```

Muito simples, fizemos um post no pushgateway enviando uma métrica some_metrics com o valor 3.322 para o jobs some_job. Isso não categoriza o tipo da métrica, para categorizar o tipo é:

```
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/some_job/instance/some_instance
# TYPE some_metric counter
some_metric{label="val1"} 42
# TYPE another_metric gauge
# HELP another_metric Just an example.
another_metric 2398.283
EOF
````

## Configurando o Prometheus para buscar as métricas

Depois disso pronto, vc precisa colocar o Pushgateway como um jobs para o prometheus poder buscar essas métricas, desse modo:

```
scrape_configs:
- job_name: pushgateway
  static_configs:
  - targets: ['localhost:9091']
```

Proto, as métricas ja vão estar disponiveis no Prometheus. Esses exemplos foram feitos com curl, mas as principais bibliotecas para o Prometheus para python, go ou outra lingaguem tem formas mais sofisticadas de enviar os dados para o pushgateway.
