# Operators

O PromQL suporta o operadoras logicos basicos e operadores de aritmética como somas e divisões.

## Operações Aritméticas

Por exemplo podemos somar duas métricas assim:

```
process_virtual_memory_bytes + process_resident_memory_bytes
```

Ou dividir uma métrica por um valor fixo assim:

```
process_resident_memory_bytes / 1024
```

## Operadores de comparação

Podemos usar operadores de comparação para extrair somente os dados que desejamos:


- == (igual)
- != (não-igual)
- > (maior-que)
- < (menor-que)
- >= (maior-ou-igual)
- <= (menor-ou-igual)


Por exemplo se quisermos ver o numero de requisições que são acima de 10 para esse metric name podemos usar assim:

```
prometheus_http_requests_total > 10
```

Ainda podemos usar os operadores aritméticos, junto com os operadores de comparação. Algo como:

```
process_virtual_memory_bytes + process_resident_memory_bytes >= 1000000
```

## Aggregation operators

O Prometheus suporta vários operadores de agregação que podem ser usados para agregar diversos elementos em um único vetor.

Os operadores de agregação mais comuns são:

- sum (calculate sum over dimensions)
- min (select minimum over dimensions)
- max (select maximum over dimensions)
- avg (calculate the average over dimensions)
- count (count number of elements in the vector)
- topk (largest k elements by sample value)


Alguns exemplos de querys são:

- `sum by (code) (prometheus_http_requests_total)` que soma todos os valores do prometheus_http_requests_total e agrega eles pela label code,
- `sum without (code) (prometheus_http_requests_total)` soma todas as métricas do prometheus_http_requests_total agregando todos os labels removendo o label code,
- `count(prometheus_http_requests_total) by (code)` conta o numero de ocorrencias da metrica prometheus_http_requests_total pelo label code,
- `topk(2,prometheus_http_requests_total)` mostra os 2 maiores valores da métrica prometheus_http_requests_total.
