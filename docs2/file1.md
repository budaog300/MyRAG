# Работа с историей чата

[source](https://developers.sber.ru/docs/ru/gigachat/guides/keeping-context.md)

Передача истории чата позволяет GigaChat работать с результатами прошлых запросов пользователя.
Когда вы переписываетесь с нейросетевой моделью в веб-интерфейсе, она автоматически учитывает историю чата.

Если для обмена сообщениями вы используете GigaChat API, историю чата нужно передавать явно в поле `messages` запроса <APIMethod type="POST" path="/chat/completions" link="/ru/gigachat/api/reference/rest/post-chat" />.

:::note

Передавайте текст сообщений (поле `content`) в кодировке UTF8.
Это позволит снизить расход токенов при обработке сообщения.

:::

<Tabs groupId="tool" queryString>
  <TabItem value="curl" label="GigaChat API" default>
    Пример запроса с историей чата:

    ```sh
    curl https://gigachat.devices.sberbank.ru/api/v1/chat/completions \
      -H 'Content-Type: application/json' \
      -H 'Authorization: Bearer access_token' \
      -d '{
      "model": "GigaChat",
      "messages": [
            {
                "role": "user",
                "content": "Когда уже ИИ захватит этот мир?"
            },
            {
                "role": "assistant",
                "content": "Пока что это не является неизбежным событием. Несмотря на то, что искусственный интеллект (ИИ) развивается быстрыми темпами и может выполнять сложные задачи все более эффективно, он по-прежнему ограничен в своих возможностях и не может заменить полностью человека во многих областях. Кроме того, существуют этические и правовые вопросы, связанные с использованием ИИ, которые необходимо учитывать при его разработке и внедрении."
            },
            {
                "role": "user",
                "content": "Думаешь, у нас еще есть шанс?"
            }
        ]
    }'
    ```
  </TabItem>

  <TabItem value="python" label="Python">
    <Tabs queryString="library">
      <TabItem value="gigachat" label="gigachat" default>
        ```py
        from gigachat import GigaChat
        from gigachat.models import Chat, Messages, MessagesRole

        with GigaChat(credentials="ключ_авторизации", verify_ssl_certs=False) as giga:
          response=giga.chat(
              Chat(
                  messages=[
                      Messages(
                          role=MessagesRole.USER,
                          content="Когда уже ИИ захватит этот мир?"
                      ),
                      Messages(
                          role=MessagesRole.ASSISTANT,
                          content="Пока что это не является неизбежным событием. Несмотря на то, что искусственный интеллект (ИИ) развивается быстрыми темпами и может выполнять сложные задачи все более эффективно, он по-прежнему ограничен в своих возможностях и не может заменить полностью человека во многих областях. Кроме того, существуют этические и правовые вопросы, связанные с использованием ИИ, которые необходимо учитывать при его разработке и внедрении."
                      ),
                      Messages(
                          role=MessagesRole.USER,
                          content="Думаешь, у нас еще есть шанс?"
                      )
                  ]
              )
          )

        print(response.choices[0].message.content)
        ```
      </TabItem>

      <TabItem value="langchain-gigachat" label="langchain-gigachat">
        ```py
        from langchain_core.messages import HumanMessage, AIMessage
        from langchain_gigachat.chat_models import GigaChat

        giga = GigaChat(
            credentials="ключ_авторизации",
            verify_ssl_certs=False,
        )

        messages = [
            HumanMessage(
                content="Когда уже ИИ захватит этот мир?"
            ),
            AIMessage(
                content="Пока что это не является неизбежным событием. Несмотря на то, что искусственный интеллект (ИИ) развивается быстрыми темпами и может выполнять сложные задачи все более эффективно, он по-прежнему ограничен в своих возможностях и не может заменить полностью человека во многих областях. Кроме того, существуют этические и правовые вопросы, связанные с использованием ИИ, которые необходимо учитывать при его разработке и внедрении."
            ),
            HumanMessage(
                content="Думаешь, у нас еще есть шанс?"
            )
        ]

        response = giga.invoke(messages)

        print(response.content)
        ```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="js" label="TS/JS">
    ```js
    import GigaChat from "gigachat";

    const giga = new GigaChat({
      credentials="ключ_авторизации",
    });

    const resp = await giga.chat({
      messages: [
        {
          role: "user",
          content: "Когда уже ИИ захватит этот мир?",
        },
        {
          role: "assistant",
          content:
            "Пока что это не является неизбежным событием. Несмотря на то, что искусственный интеллект (ИИ) развивается быстрыми темпами и может выполнять сложные задачи все более эффективно, он по-прежнему ограничен в своих возможностях и не может заменить полностью человека во многих областях. Кроме того, существуют этические и правовые вопросы, связанные с использованием ИИ, которые необходимо учитывать при его разработке и внедрении.",
        },
        {
          role: "user",
          content: "Думаешь, у нас еще есть шанс?",
        },
      ],
    });

    console.log(resp.choices[0]?.message.content);
    ```
  </TabItem>

  <TabItem value="java" label="Java">
    ```java

    public class ChatWithHistoryExample {

        public static void main(String[] args) {

            GigaChatClient client = GigaChatClient.builder()
            .authClient(AuthClient.builder()
                    .withOAuth(AuthClientBuilder.OAuthBuilder.builder()
                            .authKey("ключ_авторизации")
                            .build())
                    .build())
            .build();

            CompletionRequest.CompletionRequestBuilder builder = CompletionRequest.builder()
            .model(ModelName.GIGA_CHAT_PRO)
            .message(ChatMessage.builder()
                    .content("Когда уже ИИ захватит этот мир?")
                    .role(Role.USER)
                    .build())
            .message(ChatMessage.builder()
                    .content("Пока что это не является неизбежным событием. Несмотря на то, что искусственный интеллект (ИИ) развивается быстрыми темпами и может выполнять сложные задачи все более эффективно, он по-прежнему ограничен в своих возможностях и не может заменить полностью человека во многих областях. Кроме того, существуют этические и правовые вопросы, связанные с использованием ИИ, которые необходимо учитывать при его разработке и внедрении.")
                    .role(Role.ASSISTANT).build());

            try {
                for (int i = 0; i < 4; i++) {
                    CompletionRequest request = builder.build();
                    CompletionResponse response = client.completions(request);
                    System.out.println(response);

                    response.choices().forEach(e -> builder.message(e.message().ofAssistantMessage()));

                    builder.message(ChatMessage.builder()
                            .content("Думаешь, у нас еще есть шанс?")
                            .role(Role.USER).build());
                }
            } catch (HttpClientException ex) {
                System.out.println(ex.statusCode() + " " + ex.bodyAsString());
            }
        }
    }
    ```
  </TabItem>
</Tabs>

## Кэширование запросов

Вы можете использовать необязательный идентификатор сессии `X-Session-ID` для кэширования контекста разговора с GigaChat.
Идентификатор передается в заголовке запроса и может содержать произвольную строку.
При этом если заголовок отсутствует, сервер автоматически присвоит идентификатор сессии в формате uuid4.

Если при получении запроса, модель находит в кэше данные о запросе с таким же идентификатором и частично совпадающим контекстом, то она не пересчитывает этот контекст.
Количество кэшированных токенов, которые не учитываются в расчете стоимости, содержится в поле `precached_prompt_tokens`, в ответе на запрос <APIMethod type="POST" path="/chat/completions" link="/ru/gigachat/api/reference/rest/post-chat" />.

Кэширование позволяет повысить скорость ответа и снизить расходы на генерацию, благодаря тому, что модель тратит меньше токенов на обработку сообщений контекста с одинаковыми идентификаторами.

Подробнее о расчете стоимости — в разделе [Подсчет токенов](/ru/gigachat/guides/counting-tokens).

Кэширование может быть полезно для:

* разработки разговорных агентов, которые должны учитывать большой контекст для ведения диалога.
* создания ассистентов, которые помогают писать код. Например, вы можете закэшировать кодовую базу, которую модель должна будет учитывать при автодополнении.
* работы с большими документами.
* передачи в модель большого набора инструкций. Например, вы можете сохранить в кэше множество различных примеров желаемого результата работы модели.
* сохранения результатов вызовов функций, при многократном обращении к ним.

Примеры запросов с заголовком `X-Session-ID`.

:::note

Добавление необязательных заголовков поддерживается только в Python-библиотеках GigaChat.

:::

<Tabs groupId="tool" queryString>
  <TabItem value="curl" label="GigaChat API" default>
    Пример запроса с историей чата:

    ```sh
    curl https://gigachat.devices.sberbank.ru/api/v1/chat/completions \
      -H 'Content-Type: application/json' \
      -H 'Authorization: Bearer access_token' \
      -H 'X-Session-ID: session-id-1' \
      -d '{
      "model": "GigaChat",
      "messages": [
            {
                "role": "user",
                "content": "Запрос пользователя"
            },
            {
                "role": "assistant",
                "content": "Ответ модели"
            },
            {
                "role": "user",
                "content": "Запрос пользователя"
            }
        ],
    }'
    ```
  </TabItem>

  <TabItem value="python" label="Python">
    <Tabs queryString="library">
      <TabItem value="gigachat" label="gigachat" default>
        ```py
        import gigachat.context
        from gigachat import GigaChat

        headers = {
            "X-Session-ID": "session-id-1",
        }

        with GigaChat(
           credentials="ключ_авторизации",
           verify_ssl_certs=False
        ) as giga:
            gigachat.context.session_id_cvar.set(headers.get("X-Session-ID"))

            response = giga.chat("Какие факторы влияют на стоимость страховки на дом?")
            print(response.choices[0].message.content)
        ```
      </TabItem>

      <TabItem value="langchain-gigachat" label="langchain-gigachat">
        Синхронный вызов:

        ```py
        from gigachat import session_id_cvar
        from langchain_gigachat import GigaChat

        def main() -> None:
            llm = GigaChat(
                credentials="<ключ_авторизации>",
                model="GigaChat",
            )

            # Выставляем нужный session_id
            token = session_id_cvar.set("demo-session-001")
            try:
                response = llm.invoke("Расскажи в двух предложениях о себе.")
                print("Answer:")
                print(response.content)
            finally:
                session_id_cvar.reset(token)
        if __name__ == "__main__":
            main()
        ```

        Асинхронный вызов:

        ```py
        import asyncio
        from gigachat import session_id_cvar
        from langchain_gigachat import GigaChat
        async def main() -> None:
            llm = GigaChat(
                credentials="<ключ_авторизации>",
                model="GigaChat",
            )
            token = session_id_cvar.set("async-session-001")
            try:
                response = await llm.ainvoke("Привет! Коротко представься.")
                print(response.content)
            finally:
                session_id_cvar.reset(token)
        if __name__ == "__main__":
            asyncio.run(main())
        ```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="java" label="Java">
    ```java
    public class CompletionWithSessionIdExample {

        public static void main(String[] args) {

            GigaChatClient client = GigaChatClient.builder()
                    .verifySslCerts(false)
                    .authClient(AuthClient.builder()
                            .withOAuth(OAuthBuilder.builder()
                                    .scope(Scope.GIGACHAT_API_PERS)
                                    .authKey("ключ_авторизации")
                                    .build())
                            .build())
                    .build();
            try {
                System.out.println(client.completions(CompletionRequest.builder()
                        .model(ModelName.GIGA_CHAT_MAX)
                        .message(ChatMessage.builder()
                                .content("Какие факторы влияют на стоимость страховки на дом?")
                                .role(Role.USER)
                                .build())
                        .build(), "session-id-1"));
            } catch (HttpClientException ex) {
                System.out.println(ex.statusCode() + " " + ex.bodyAsString());
            }
        }
    }
    ```
  </TabItem>
</Tabs>
