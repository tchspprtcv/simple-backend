# Code Generator Documentation

## Introdução

O `code_generator.py` é um script Python projetado para automatizar a criação de código boilerplate no projeto `simple-backend`. Ele lê configurações definidas em formato JSON, localizadas no diretório `.igrpstudio`, e gera diversas classes Java, como entidades, DTOs, repositórios, mappers, comandos, queries e controladores.

### Para que serve?

No contexto do projeto `simple-backend`, este gerador tem como principal objetivo:

*   **Acelerar o desenvolvimento:** Reduzir o tempo gasto na escrita de código repetitivo para cada nova entidade ou funcionalidade.
*   **Padronizar a estrutura do código:** Garantir que as classes geradas sigam uma arquitetura e convenções consistentes em todo o projeto.
*   **Minimizar erros:** Diminuir a probabilidade de erros manuais na criação das estruturas básicas das classes.
*   **Facilitar a manutenção:** Com uma estrutura padronizada, a compreensão e manutenção do código tornam-se mais simples.

Ao utilizar o gerador, os desenvolvedores podem focar mais na lógica de negócios específica da aplicação, deixando a cargo do script a criação da infraestrutura básica de cada módulo.

## Pré-requisitos

Antes de utilizar o gerador de código, certifique-se de que os seguintes pré-requisitos são atendidos:

### 1. Software Necessário

*   **Java Development Kit (JDK):** Versão 11 ou superior. O projeto `simple-backend` é baseado em Java, e o código gerado é compatível com esta versão.
*   **Apache Maven:** Utilizado para gerenciamento de dependências e build do projeto Java. Certifique-se de que o Maven está instalado e configurado corretamente no seu ambiente.
*   **Python:** Versão 3.6 ou superior, para executar o script `code_generator.py`.
*   **Jinja2:** Biblioteca Python de templating. Se não estiver instalada, você pode instalá-la via pip:
    ```bash
    pip install Jinja2
    ```

### 2. Estrutura do Projeto

O gerador espera uma estrutura de diretórios específica para ler as configurações:

*   **`.igrpstudio/`**: Este diretório na raiz do projeto é fundamental. É onde todas as configurações para a geração de código são armazenadas.
    *   **`.igrpstudio/<NomeDoModulo>/`**: Cada módulo da sua aplicação (ex: `pedidos`, `utente`, `configuracoes`) deve ter seu próprio subdiretório dentro de `.igrpstudio`.
        *   **`models/`**: Contém os arquivos JSON que definem as entidades (ex: `EntidadeExemplo.json`).
        *   **`controllers/`**: Contém os arquivos JSON que definem os controladores e suas actions (ex: `EntidadeExemploController.json`).
        *   **`enums/`**: (Opcional) Contém os arquivos JSON que definem enums específicos do módulo (ex: `StatusPedido.json`).
*   **`templates/`**: Este diretório na raiz do projeto contém os templates Jinja2 (`.j2` arquivos) que o gerador usa para criar os arquivos Java. A estrutura padrão já fornecida no projeto deve ser mantida.
*   **`src/main/java/`**: Embora o gerador escreva por padrão no diretório `generated_output` (configurável), o código gerado é projetado para ser eventualmente movido ou integrado à estrutura de código fonte principal do Java, tipicamente sob `src/main/java/cv/igrp/simple/<nomedomodulo_minusculo>/...`.

### 3. Configurações JSON

*   Os arquivos de configuração (`.json`) dentro do diretório `.igrpstudio` podem ser criados e editados manualmente, seguindo a estrutura detalhada nas seções seguintes.
*   Alternativamente, se o projeto utilizar o IGRP Studio como ferramenta de modelagem visual, essas configurações podem ser exportadas ou gerenciadas através dele, garantindo que o formato JSON seja compatível com o esperado pelo gerador.

## Como Preparar a Configuração

A geração de código é inteiramente baseada nos arquivos de configuração JSON localizados no diretório `.igrpstudio`. É crucial que estes arquivos sigam a estrutura esperada pelo gerador.

### 1. Estrutura Geral do Módulo

Dentro de `.igrpstudio/<NomeDoModulo>/`, você encontrará (ou precisará criar) as seguintes subpastas:

*   `models/`: Para definições de entidades.
*   `controllers/`: Para definições de controladores.
*   `enums/`: (Opcional) Para definições de tipos enumerados.

### 2. Configuração de Entidades (`models/*.json`)

Os arquivos JSON em `models/` definem as entidades do seu domínio. O nome do arquivo geralmente corresponde ao nome da entidade (ex: `Produto.json` para uma entidade `Produto`).

**Exemplo de Configuração de Entidade (`.igrpstudio/pedidos/models/PedidosEntity.json` simplificado):**

```json
{
  "name": "PedidosEntity", // Nome da entidade, geralmente terminando com "Entity"
  "tableName": "tbl_pedidos", // Nome da tabela no banco de dados
  "attributes": [
    {
      "name": "id",
      "type": "long", // Tipos: string, integer, long, date, datetime, boolean, double, decimal, relation, etc.
      "primaryKey": true,
      "generationType": "IDENTITY" // Ex: "IDENTITY", "SEQUENCE", "AUTO" (JPA GenerationType)
    },
    {
      "name": "descricao",
      "type": "string",
      "length": 255,
      "nullable": false // true se o campo puder ser nulo
    },
    {
      "name": "data_pedido",
      "type": "datetime",
      "nullable": false
    },
    {
      "name": "status_pedido", // Exemplo de um campo que seria um Enum
      "type": "StatusPedido", // Nome do Enum (definido em enums/)
      "objectType": "enum", // Indica que este campo é um enum
      "nullable": false
    },
    {
      "name": "utente", // Nome do campo na entidade PedidosEntity
      "type": "relation", // Indica um relacionamento
      "relation": {
        "entity": "UtenteEntity", // Entidade relacionada (deve existir em .igrpstudio/<modulo>/models/)
        "type": "ManyToOne", // Tipo de relação: ManyToOne, OneToMany, OneToOne
        "mappedBy": null // Para OneToMany, nome do campo na entidade UtenteEntity que mapeia de volta. Para ManyToOne/OneToOne, geralmente null aqui.
      },
      "nullable": true
    }
  ]
}
```

**Campos Importantes para Atributos:**

*   `name`: (Obrigatório) Nome do atributo na classe Java (será convertido para lowerCamelCase). O `code_generator.py` também usa este nome para `column_name` por padrão.
*   `type`: (Obrigatório) Tipo do dado. O script `map_type` tentará converter para um tipo Java.
    *   Tipos comuns: `string`, `text`, `integer`, `number` (para Integer), `long`, `date`, `datetime`, `boolean`, `double`, `float`, `decimal`, `bigdecimal`, `binary`.
    *   Para relacionamentos: `relation`.
    *   Para enums: O nome do enum como definido no arquivo JSON do enum (ex: `StatusPedido`).
*   `primaryKey` (Boolean): `true` se for a chave primária.
*   `generationType` (String): Estratégia de geração para chaves primárias (ex: `IDENTITY`, `AUTO`).
*   `length` (Integer): Para campos do tipo String, define o comprimento da coluna.
*   `nullable` (Boolean): `true` se o campo pode ser nulo, `false` caso contrário. Se `nullable` for `false` para tipos `string` ou `text`, uma anotação `@NotBlank` pode ser adicionada.
*   `objectType` (String): Usado especificamente para enums. Defina como `"enum"`.
*   `relation` (Object): Obrigatório se `type` for `"relation"`.
    *   `entity` (String): O nome da entidade relacionada (ex: `UtenteEntity`).
    *   `type` (String): `OneToMany`, `ManyToOne`, `OneToOne`.
    *   `mappedBy` (String): Para `OneToMany`, especifica o campo na entidade "Many" que possui a anotação `@ManyToOne` e "dona" da relação.

**Convenções de Nomes:**

*   Nomes de entidades no JSON (`name`) geralmente são em PascalCase e terminam com "Entity" (ex: `PedidosEntity`). O gerador extrairá o nome base (ex: `Pedidos`) para outras classes (DTOs, Controllers, etc.).
*   Nomes de atributos no JSON (`name`) podem ser em snake_case ou camelCase; o gerador os converterá para lowerCamelCase nas classes Java.

### 3. Configuração de Enums (`enums/*.json`)

Arquivos em `enums/` definem tipos enumerados.

**Exemplo de Configuração de Enum (`.igrpstudio/pedidos/enums/StatusPedido.json`):**

```json
{
  "name": "StatusPedido", // Nome do Enum em PascalCase
  "values": [ // Lista de valores do enum
    "PENDENTE",
    "EM_PROCESSAMENTO",
    "CONCLUIDO",
    "CANCELADO"
  ]
}
```
Ou, com mais detalhes (o gerador suporta isso também, embora a documentação foque no mais simples):
```json
{
  "name": "TipoPrioridade",
  "value_details_structure": { // Opcional: define a estrutura dos detalhes
    "label": "String",
    "color": "String"
  },
  "values": [
    { "name": "ALTA", "details": { "label": "Alta Prioridade", "color": "red" } },
    { "name": "MEDIA", "details": { "label": "Média Prioridade", "color": "orange" } },
    { "name": "BAIXA", "details": { "label": "Baixa Prioridade", "color": "green" } }
  ]
}
```

### 4. Configuração de Controladores (`controllers/*.json`)

Arquivos em `controllers/` definem os endpoints da API REST. O nome do arquivo geralmente é `<NomeDaEntidadePrincipal>Controller.json`.

**Exemplo de Configuração de Controlador (`.igrpstudio/pedidos/controllers/PedidosController.json` simplificado):**

```json
{
  "name": "PedidosController", // Nome do Controller, geralmente <Entidade>Controller
  "basePath": "/api/v1/pedidos", // Path base para todos os endpoints deste controller
  "description": "Controller para gerenciar Pedidos", // Usado para tags OpenAPI/Swagger
  "actions": [
    {
      "actionName": "listarTodosOsPedidos", // Nome da ação, será convertido para nome de método
      "httpMethod": "GET", // GET, POST, PUT, DELETE
      "path": "", // Relativo ao basePath. Vazio aqui significa /api/v1/pedidos
      "requestParams": [ // Para GET com query params ou POST/PUT com DTOs (o gerador foca em query params para GET)
        { "name": "dataInicio", "type": "date", "isRequired": false },
        { "name": "status", "type": "string", "isRequired": false }
      ]
    },
    {
      "actionName": "obterPedidoPorId",
      "httpMethod": "GET",
      "path": "/{id}"
    },
    {
      "actionName": "criarNovoPedido",
      "httpMethod": "POST",
      "path": ""
    },
    {
      "actionName": "atualizarPedidoExistente",
      "httpMethod": "PUT",
      "path": "/{id}"
    },
    {
      "actionName": "removerPedido",
      "httpMethod": "DELETE",
      "path": "/{id}"
    }
  ]
}
```

**Campos Importantes para Controladores:**

*   `name`: (Obrigatório) Nome do controlador. O gerador infere a entidade principal a partir deste nome (removendo "Controller").
*   `basePath`: (Obrigatório) URL base para os endpoints.
*   `description`: Descrição para documentação da API.
*   `actions`: (Obrigatório) Lista de ações/endpoints.
    *   `actionName`: (Obrigatório) Nome da ação (será convertido para `lowerCamelCase` para o nome do método Java). O gerador usa este nome para inferir o tipo de operação (criar, listar, obter, atualizar, deletar).
    *   `httpMethod`: (Obrigatório) `GET`, `POST`, `PUT`, `DELETE`.
    *   `path`: (Obrigatório) Path do endpoint, relativo ao `basePath`. Pode incluir variáveis de path como `{id}`.
    *   `requestParams` (Array): Usado principalmente para definir query parameters para actions `GET` que listam recursos.
        *   `name`: Nome do parâmetro.
        *   `type`: Tipo do parâmetro.
        *   `isRequired` (Boolean): Se o parâmetro é obrigatório.

Ao definir essas configurações cuidadosamente, você pode gerar uma base sólida para os módulos da sua aplicação.

## Como Executar a Geração

Após preparar os arquivos de configuração JSON no diretório `.igrpstudio` para o seu módulo, você pode executar o script `code_generator.py` para gerar o código Java.

### Comando Básico

O script é executado a partir da raiz do projeto usando Python:

```bash
python code_generator.py <NomeDoModulo>
```

**Argumentos:**

*   `<NomeDoModulo>`: (Obrigatório) Este é o nome do diretório do módulo dentro de `.igrpstudio` para o qual você deseja gerar o código. Por exemplo, se suas configurações estão em `.igrpstudio/pedidos/`, então `<NomeDoModulo>` será `pedidos`. O nome do módulo é case-sensitive e deve corresponder exatamente ao nome da pasta.

### Argumentos Opcionais

O script aceita alguns argumentos opcionais para customizar o processo de geração:

*   `--output_dir <diretorio_de_saida>`:
    *   Especifica o diretório base onde o código gerado será salvo.
    *   **Padrão:** `generated_output` (ou seja, se não especificado, o código será gerado em uma pasta `generated_output` na raiz do projeto).
    *   Exemplo: `python code_generator.py pedidos --output_dir src/main/java` (Cuidado: isso escreveria diretamente na sua pasta de fontes, o que pode ser desejado, mas certifique-se de controlar as alterações com Git).

*   `--template_dir <diretorio_de_templates>`:
    *   Especifica o diretório onde os arquivos de template Jinja2 (`.j2`) estão localizados.
    *   **Padrão:** `templates` (ou seja, espera-se que exista uma pasta `templates` na raiz do projeto).
    *   Normalmente, você não precisará alterar este argumento, a menos que tenha uma estrutura de templates customizada.

### Exemplo de Execução

Para gerar o código para um módulo chamado `pedidos`, cujas configurações estão em `.igrpstudio/pedidos/`, e utilizando os diretórios padrão para saída e templates, execute:

```bash
python code_generator.py pedidos
```

Após a execução, você verá mensagens no console indicando quais arquivos foram gerados e se houve algum erro ou aviso durante o processo. O código gerado estará em `generated_output/pedidos/`.

Se você quisesse gerar o código para um módulo `utente` diretamente na pasta de código fonte principal (assumindo a estrutura de pacotes `cv.igrp.simple`):

```bash
python code_generator.py utente --output_dir src/main/java/cv/igrp/simple
```
**Nota:** Ao usar `--output_dir` para apontar diretamente para `src/main/java/...`, certifique-se de que o caminho final (`cv/igrp/simple` neste exemplo) corresponda à estrutura de pacotes base definida nos templates (que é `cv.igrp.simple` por padrão). O gerador criará a subpasta do módulo (ex: `utente`) dentro do diretório de saída especificado.

## Estrutura do Código Gerado

Ao executar o `code_generator.py`, os arquivos Java são criados em uma estrutura de diretórios e pacotes específica, por padrão dentro da pasta `generated_output` (ou no diretório especificado por `--output_dir`).

### Diretório de Saída

Por padrão, todo o código gerado para um módulo é colocado em:

`generated_output/<NomeDoModulo>/`

Onde `<NomeDoModulo>` é o nome do módulo que você passou como argumento para o script (ex: `pedidos`).

Dentro desta pasta, o código é organizado de acordo com uma arquitetura em camadas:

### Estrutura de Pacotes Java

O pacote base para todo o código gerado é `cv.igrp.simple.<nomedomodulo_minusculo>`. Por exemplo, para um módulo `Pedidos`, o pacote base será `cv.igrp.simple.pedidos`.

Abaixo do pacote base, as classes são organizadas da seguinte forma:

*   **Entidades e Enums:**
    *   Localização: `domain/models/`
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.domain.models`
    *   Exemplos: `ProdutoEntity.java`, `StatusPedido.java`
    *   Anotações Comuns (inferidas das entidades JPA): `@Entity`, `@Table`, `@Id`, `@GeneratedValue`, `@Column`, `@ManyToOne`, `@OneToMany`, `@Enumerated`.

*   **Repositórios:**
    *   Localização: `domain/repository/`
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.domain.repository`
    *   Exemplos: `IProdutoRepository.java`
    *   Anotações Comuns: `@Repository` (geralmente em implementações, a interface gerada é pura). Estende `JpaRepository`.

*   **DTOs (Data Transfer Objects):**
    *   Localização: `application/dto/`
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.application.dto`
    *   Exemplos: `ProdutoResponseDTO.java`, `CreateProdutoDTO.java`, `UpdateProdutoDTO.java`
    *   Anotações Comuns: Podem incluir anotações de validação como `@NotNull`, `@NotBlank` (se `nullable:false` na config), `@Size` (se `length` na config). Lombok anotações como `@Data`, `@Builder` são comuns se usadas nos templates.

*   **Mappers:**
    *   Localização: `application/mapper/`
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.application.mapper`
    *   Exemplos: `ProdutoMapper.java`
    *   Anotações Comuns: Frequentemente usam MapStruct (`@Mapper`).

*   **Comandos (CQRS):**
    *   Localização: `application/commands/<acao><Entidade>/` (ex: `application/commands/createProduto/`)
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.application.commands.<acao><Entidade>`
    *   Exemplos: `CreateProdutoCommand.java`, `CreateProdutoCommandHandler.java`
    *   Anotações Comuns: `@Service` ou `@Component` nos Handlers.

*   **Queries (CQRS):**
    *   Localização: `application/queries/<acao><Entidade>/` (ex: `application/queries/listProduto/` ou `application/queries/getProdutoById/`)
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.application.queries.<acao><Entidade>`
    *   Exemplos: `ListaDeProdutoQuery.java`, `ListaDeProdutoQueryHandler.java`, `GetProdutoByIdQuery.java`, `GetProdutoByIdQueryHandler.java`
    *   Anotações Comuns: `@Service` ou `@Component` nos Handlers.

*   **Controladores:**
    *   Localização: `infrastructure/controller/`
    *   Pacote Java: `cv.igrp.simple.<nomedomodulo_minusculo>.infrastructure.controller`
    *   Exemplos: `ProdutoController.java`
    *   Anotações Comuns (Spring MVC/Web): `@RestController`, `@RequestMapping`, `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PathVariable`, `@RequestBody`, `@RequestParam`. Anotações OpenAPI/Swagger como `@Tag`, `@Operation` também são geradas com base na configuração do controller.

Compreender esta estrutura ajuda a localizar rapidamente os arquivos gerados e a integrá-los ao seu projeto principal. Se você alterar o diretório de saída para `src/main/java/cv/igrp/simple`, o gerador criará a pasta do módulo (ex: `pedidos`) e toda essa estrutura dentro dela.

## Validações e Boas Práticas

Para garantir que o processo de geração de código ocorra sem problemas e que o código gerado seja útil e correto, siga estas validações e boas práticas:

### Antes da Geração

1.  **Valide a Sintaxe JSON:** Certifique-se de que todos os seus arquivos de configuração `.json` são sintaticamente válidos. Um único erro de JSON (como uma vírgula faltando ou uma chave mal formatada) pode impedir o processamento do arquivo. Utilize um validador de JSON online ou a funcionalidade de linting da sua IDE.
2.  **Verifique Nomes e Caminhos:**
    *   Confirme se o nome do módulo fornecido ao script corresponde exatamente ao nome da pasta em `.igrpstudio/`.
    *   Verifique se os nomes dos arquivos JSON dentro de `models/`, `controllers/`, e `enums/` estão corretos e são consistentes.
3.  **Confira os Tipos de Dados:** Revise os tipos de dados (`type`) especificados para os atributos das entidades e parâmetros de request. Um tipo incorreto pode levar a erros de compilação no código Java gerado ou a um comportamento inesperado. Consulte a seção `map_type` no script `code_generator.py` para entender como os tipos são mapeados.
4.  **Relacionamentos Entre Entidades:**
    *   Ao definir relacionamentos (`relation`), assegure-se de que a entidade referenciada (`entity`) existe e está corretamente configurada em seu próprio arquivo JSON.
    *   Para relacionamentos `OneToMany`, verifique se o campo `mappedBy` corresponde a um atributo existente na entidade do lado "Many".
5.  **Campos Obrigatórios:** Certifique-se de que todos os campos obrigatórios nas configurações JSON estão presentes. Por exemplo, `name` e `type` para atributos de entidade, `name` e `actions` para controllers, etc.
6.  **Consistência nos Nomes:** Mantenha uma convenção de nomes consistente. Embora o gerador faça conversões de case (snake_case para camelCase, etc.), começar com nomes claros e consistentes nos JSONs facilita a compreensão.

### Após a Geração

1.  **Revise o Código Gerado:**
    *   **Não confie cegamente.** Embora o gerador automatize muito trabalho, é sempre uma boa prática revisar o código gerado, especialmente para entidades complexas ou controllers com lógica específica.
    *   Verifique se os tipos de dados Java correspondem ao esperado.
    *   Confirme se os relacionamentos entre entidades foram gerados corretamente (anotações `@ManyToOne`, `@OneToMany`, etc.).
    *   Analise as DTOs, Mappers, Comandos, Queries e Controllers para garantir que a estrutura básica atende às suas necessidades.
2.  **Teste o Código:** Integre o código gerado ao seu projeto e escreva testes unitários e de integração para validar a funcionalidade.
3.  **Gerenciamento com Git:**
    *   **Commit antes de gerar:** Antes de executar o gerador, especialmente se você estiver regenerando um módulo existente, faça commit de todas as suas alterações pendentes. Isso permite que você veja claramente o que o gerador modificou e reverta se necessário.
    *   **Revise as `diffs`:** Após a geração, use `git diff` para ver as alterações. Isso é especialmente importante se você estiver gerando diretamente na sua pasta `src/main/java`.
4.  **Entenda o Processo de Sobrescrita:** O gerador tipicamente sobrescreve arquivos existentes com o mesmo nome no diretório de saída. Se você fez modificações manuais em um arquivo gerado e depois regenerar, suas modificações serão perdidas. Considere estratégias para lidar com isso (veja FAQs).
5.  **Ajustes Manuais:** É comum que o código gerado sirva como uma excelente base, mas precise de ajustes manuais para adicionar lógica de negócios específica, validações mais complexas ou otimizações.

Seguindo estas práticas, você maximizará os benefícios do gerador de código e minimizará possíveis problemas.

## Erros Comuns e Como Resolver

Durante a utilização do gerador de código, você pode encontrar alguns erros comuns. Aqui estão os mais frequentes e como resolvê-los:

1.  **Erro: `FileNotFoundError` ou Mensagem de Diretório `.igrpstudio` ou Módulo Não Encontrado**
    *   **Causa:** O script não conseguiu encontrar o diretório `.igrpstudio` na raiz do projeto, ou o subdiretório do módulo especificado (ex: `.igrpstudio/<NomeDoModulo>`).
    *   **Resolução:**
        *   Verifique se você está executando o script `code_generator.py` a partir do diretório raiz do seu projeto.
        *   Confirme se o diretório `.igrpstudio` existe na raiz.
        *   Certifique-se de que o `<NomeDoModulo>` fornecido como argumento ao script corresponde exatamente ao nome da pasta dentro de `.igrpstudio` (é case-sensitive).
        *   Verifique se as subpastas esperadas (`models/`, `controllers/`) existem dentro da pasta do módulo, caso o erro seja mais específico sobre não encontrar arquivos de configuração.

2.  **Erro: `json.decoder.JSONDecodeError` ou Erro de Parsing de JSON**
    *   **Causa:** Um dos arquivos `.json` de configuração (para entidades, controllers ou enums) contém erros de sintaxe.
    *   **Resolução:**
        *   O script geralmente indica qual arquivo JSON está causando o problema.
        *   Abra o arquivo problemático e valide sua sintaxe. Use uma IDE com linting de JSON ou um validador online.
        *   Procure por vírgulas faltando ou sobrando, chaves `{}` ou colchetes `[]` desbalanceados, ou aspas incorretas.

3.  **Aviso: `Warning: Type '<nome_do_tipo>' is unknown... Defaulting to 'Object'.`**
    *   **Causa:** Você especificou um `type` para um atributo em um arquivo JSON de entidade que não é reconhecido pela função `map_type` no `code_generator.py`.
    *   **Resolução:**
        *   Verifique a grafia do tipo no seu arquivo JSON.
        *   Consulte a lista de tipos suportados na seção "Configuração de Entidades" desta documentação ou diretamente na função `map_type` do script.
        *   Se for um tipo customizado que deveria ser um Enum, certifique-se de que `objectType: "enum"` está especificado e que o enum está definido corretamente.
        *   Se for um relacionamento, certifique-se de que `type: "relation"` está correto e a sub-configuração `relation` está presente.
        *   Se for um novo tipo primitivo ou de biblioteca que você deseja suportar, pode ser necessário estender a função `map_type` no script `code_generator.py`.

4.  **Problema: Código Gerado Sobrescreve Modificações Manuais**
    *   **Causa:** O gerador de código normalmente sobrescreve os arquivos existentes no diretório de saída. Se você modificou manualmente um arquivo gerado (ex: `ProdutoEntity.java`) e depois rodar o gerador novamente para o mesmo módulo, suas alterações manuais serão perdidas.
    *   **Resolução:**
        *   **Versionamento:** Sempre faça commit das suas alterações no Git antes de executar o gerador. Isso permite que você compare as versões e reverta, se necessário.
        *   **Geração em Diretório Separado:** Gere o código em um diretório temporário (usando `--output_dir`) e depois use uma ferramenta de `diff/merge` para incorporar as alterações no seu código fonte principal, preservando suas modificações manuais.
        *   **Herança ou Classes Parciais (se aplicável à linguagem/framework):** Para algumas customizações, você pode criar classes que herdam das classes geradas ou usar outros mecanismos para separar o código customizado.
        *   **Edição dos Templates:** Se a modificação é algo que você sempre vai querer, considere editar os templates Jinja2 (`.j2`) para que o código seja gerado da maneira desejada.

5.  **Problema: Relacionamentos Entre Entidades Não Funcionam Como Esperado**
    *   **Causa:** Configuração incorreta da seção `relation` no JSON da entidade.
    *   **Resolução:**
        *   Verifique se `entity` na configuração da relação aponta para o nome correto da entidade JSON (ex: `UtenteEntity`).
        *   Confirme o tipo de relação: `OneToMany`, `ManyToOne`, `OneToOne`.
        *   Para `OneToMany`, o campo `mappedBy` é crucial. Ele deve corresponder ao nome do atributo na entidade "filha" que estabelece a relação `@ManyToOne`.
        *   Verifique se as anotações JPA (`@JoinColumn`, etc.) foram geradas como esperado. Pode ser necessário ajustar a configuração JSON ou os templates para casos mais complexos.

6.  **Erro de Template Jinja2 (`jinja2.exceptions.TemplateNotFound`, `jinja2.exceptions.TemplateSyntaxError`, etc.)**
    *   **Causa:** O template referenciado no script Python não foi encontrado no `template_dir` (padrão: `templates/`), ou o template em si tem erros de sintaxe Jinja2.
    *   **Resolução:**
        *   Verifique se o `template_dir` está correto e contém todos os arquivos `.j2` necessários.
        *   Se for `TemplateSyntaxError`, a mensagem de erro geralmente aponta para a linha e o tipo de problema no arquivo de template. Edite o arquivo `.j2` para corrigir a sintaxe.

Ao encontrar um erro não listado aqui, examine a mensagem de erro completa fornecida pelo script, pois ela geralmente contém pistas sobre o arquivo ou a configuração problemática.

## Exemplo Completo

Para ilustrar o processo, vamos criar um exemplo simples de uma entidade `Livro` com algumas propriedades básicas e ver a configuração JSON e o código Java gerado.

### 1. Configuração de Entrada

Suponha que no módulo `biblioteca`, criamos o seguinte arquivo de configuração:

**`.igrpstudio/biblioteca/models/LivroEntity.json`**:

```json
{
  "name": "LivroEntity",
  "tableName": "tbl_livros",
  "attributes": [
    {
      "name": "id",
      "type": "long",
      "primaryKey": true,
      "generationType": "IDENTITY"
    },
    {
      "name": "titulo",
      "type": "string",
      "length": 200,
      "nullable": false
    },
    {
      "name": "autor",
      "type": "string",
      "length": 150,
      "nullable": true
    },
    {
      "name": "ano_publicacao",
      "type": "integer",
      "nullable": true
    },
    {
      "name": "isbn",
      "type": "string",
      "length": 20,
      "nullable": true,
      "column_name": "codigo_isbn" // Exemplo de nome de coluna customizado
    }
  ]
}
```

(Para este exemplo, não vamos criar um `LivroController.json` ou outros arquivos, focando apenas na geração da entidade a partir deste JSON.)

### 2. Comando de Geração

Para gerar o código para o módulo `biblioteca`, executaríamos:

```bash
python code_generator.py biblioteca
```

### 3. Código de Saída Esperado (Entidade)

Após a execução, um dos arquivos gerados seria `generated_output/biblioteca/domain/models/LivroEntity.java`. O conteúdo esperado (baseado nos templates padrão) seria similar a este:

```java
package cv.igrp.simple.biblioteca.domain.models;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank; // Se nullable:false e type:string
import jakarta.validation.constraints.Size;    // Se length é especificado

// Lombok annotations como @Data, @Getter, @Setter, @NoArgsConstructor, @AllArgsConstructor
// podem estar presentes dependendo da configuração dos templates.
// Vamos assumir que elas são adicionadas pelos templates para brevidade.
// import lombok.Data;

// @Data // Exemplo se Lombok fosse usado
@Entity
@Table(name = "tbl_livros")
public class LivroEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @NotBlank // Gerado porque nullable é false e o tipo é string
    @Size(max = 200) // Gerado por causa do 'length'
    @Column(name = "titulo", nullable = false, length = 200)
    private String titulo;

    @Size(max = 150)
    @Column(name = "autor", length = 150) // nullable = true por padrão se não especificado no @Column
    private String autor;

    @Column(name = "ano_publicacao")
    private Integer anoPublicacao;

    @Size(max = 20)
    @Column(name = "codigo_isbn", length = 20) // Usa 'column_name' do JSON
    private String isbn;

    // Construtores, Getters e Setters seriam gerados aqui
    // (ou fornecidos por Lombok se configurado nos templates)

    public LivroEntity() {
    }

    public LivroEntity(String titulo, String autor, Integer anoPublicacao, String isbn) {
        this.titulo = titulo;
        this.autor = autor;
        this.anoPublicacao = anoPublicacao;
        this.isbn = isbn;
    }

    // Exemplo de Getters e Setters (seriam gerados para todos os campos)
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public String getAutor() {
        return autor;
    }

    public void setAutor(String autor) {
        this.autor = autor;
    }

    public Integer getAnoPublicacao() {
        return anoPublicacao;
    }

    public void setAnoPublicacao(Integer anoPublicacao) {
        this.anoPublicacao = anoPublicacao;
    }

    public String getIsbn() {
        return isbn;
    }

    public void setIsbn(String isbn) {
        this.isbn = isbn;
    }

    // hashCode, equals, toString podem ser gerados também
}
```

Este exemplo demonstra como uma configuração JSON simples para uma entidade é transformada em um arquivo Java `*Entity.java` completo com as anotações JPA e de validação apropriadas. Similarmente, se tivéssemos definido DTOs, repositório, mapper e controller, estes também seriam gerados com base em suas respectivas configurações e templates.

## FAQs ou Dicas rápidas

Aqui estão algumas perguntas frequentes e dicas rápidas para ajudar no uso do gerador de código:

**P1: Posso editar os arquivos gerados?**

*   **R:** Sim, você pode editar os arquivos gerados. No entanto, esteja ciente de que **se você executar o gerador novamente para o mesmo módulo, suas alterações manuais nos arquivos gerados anteriormente serão sobrescritas.**
*   **Estratégias:**
    *   **Commit Frequente:** Sempre faça commit das suas alterações no Git antes de regenerar. Assim, você pode ver o que foi alterado e decidir se deseja manter suas edições ou as novas versões geradas.
    *   **Geração em Diretório Temporário:** Gere o código em um diretório de saída temporário (usando `--output_dir ./temp_generated_code`) e depois use uma ferramenta de `diff/merge` (como a da sua IDE ou `meld`, `kdiff3`) para mesclar as alterações nos seus arquivos de código fonte principais. Isso lhe dá controle total sobre o que é sobrescrito.
    *   **Herança/Composição:** Para adicionar funcionalidades sem alterar diretamente o código gerado, considere criar classes que herdam das classes geradas ou que as utilizam por composição.
    *   **Edite os Templates:** Se a modificação é algo que você deseja aplicar a todo o código gerado desse tipo, a melhor abordagem a longo prazo é editar os templates Jinja2 (`.j2`) na pasta `templates/`.

**P2: Como versionar as configurações do `.igrpstudio` no Git?**

*   **R:** Simplesmente adicione e faça commit do diretório `.igrpstudio` e todo o seu conteúdo (arquivos JSON de módulo, modelo, controller, enum) ao seu repositório Git.
*   **Boas Práticas:**
    *   Trate esses arquivos de configuração como parte integrante do código fonte do seu projeto.
    *   Ao fazer alterações nas configurações (ex: adicionar um novo atributo a uma entidade), faça commit dessas alterações com mensagens claras.
    *   Isso garante que toda a equipe tenha acesso às mesmas configurações e que o histórico de mudanças na estrutura da sua aplicação seja rastreável.

**P3: O gerador parece lento para módulos muito grandes. Há algo que eu possa fazer?**

*   **R:** A geração envolve leitura de múltiplos arquivos, parsing de JSON, e renderização de templates, o que pode levar algum tempo para módulos com muitas entidades e controllers.
*   **Dicas:**
    *   **Gere por Módulo:** O script já opera no nível do módulo, o que é a principal forma de granularidade. Evite tentar gerar "tudo de uma vez" se não for necessário.
    *   **Hardware:** Uma máquina mais rápida (CPU, SSD) naturalmente processará mais rápido.
    *   **Otimização do Script (Avançado):** Se se tornar um gargalo significativo, o script Python em si poderia ser perfilado e otimizado, mas isso seria um esforço de desenvolvimento considerável.

**P4: Como posso adicionar um novo tipo de dado que não é suportado pela função `map_type`?**

*   **R:** Você precisará editar o script `code_generator.py`.
    1.  Abra o arquivo `code_generator.py`.
    2.  Localize a função `map_type(igrp_type, attr_config=None)`.
    3.  Adicione uma nova entrada ao dicionário `mapping` ou adicione uma nova condição `if/elif` para o seu tipo customizado, retornando a string correspondente ao tipo Java completo (ex: `com.minhabiblioteca.MeuTipoCustomizado`).
    4.  Certifique-se de que a classe Java correspondente esteja disponível no classpath do projeto gerado.

**P5: Posso customizar os templates de geração?**

*   **R:** Sim! Esta é uma das grandes vantagens do gerador. Os templates estão na pasta `templates/` e são arquivos `.java.j2` (Jinja2).
*   Você pode modificar os templates existentes para alterar a estrutura do código gerado, adicionar ou remover anotações, mudar a formatação, etc.
*   **Cuidado:** Faça um backup dos templates originais antes de modificá-los extensivamente, ou trabalhe em um branch separado do Git. Entender a sintaxe do Jinja2 será necessário.

**P6: Onde devo colocar o código de negócio específico que não é gerado?**

*   **R:** O código gerado (Entidades, Repositórios básicos, DTOs, Mappers, Controllers básicos, Comandos/Queries CQRS) forma a camada de infraestrutura e aplicação básica.
*   A lógica de negócio mais complexa, validações específicas, orquestração de serviços, ou qualquer comportamento que não seja puramente CRUD, geralmente pertence a:
    *   **Classes de Serviço/Use Case:** (Que podem usar os repositórios e mappers gerados).
    *   **Handlers de Comando/Query:** Os handlers gerados são básicos. Você frequentemente os estenderá com lógica de negócios.
    *   **Métodos customizados em Entidades:** Para lógica intrínseca à entidade.
    *   **Novas classes:** Que interagem com os componentes gerados.
    O ideal é manter uma separação clara entre o código gerado (que pode ser sobrescrito) e o seu código customizado.
