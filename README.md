# susie

> The project is named after *Susie* from *Lord of the Mysteries*.  
> She is Audrey’s golden retriever, as well as her friend and trusted assistant.  
> See https://lordofthemysteries.fandom.com/wiki/Susie for more details.

**Chat with agents on Telegram through ACP.**

This project lets agents handle Telegram requests on my behalf through my personal account rather than through a bot.

> [!CAUTION]
> This project is under active development.

## Quick Start

### 1. Install

```bash
uv tool install git+https://github.com/AFutureD/tele-acp
```

### 2. Log in to Telegram

To let Susie receive messages from Telegram, you need to log in first.
This will also update the channel settings in the configuration file.

```bash
susie auth login
susie auth me
```

### 3. Start the service

```bash
susie start
```

### 4. Configuration

After starting the service, you can adjust the configuration to match your needs.

There are two parts.

**Part one: ACP**

You should manage your agent directly rather than through Susie.

The working directory is `~/.config/susie/workspace/<YOUR_AGENT_ID>`.

> [!NOTE]
> You can change the working directory in Susie's configuration.


**Part two: Susie**


Susie's configuration file is located at `~/.config/susie/config.toml`.

After you log in to Telegram, this file should already be created for you.

See [Configuration](./docs/Configutation.md) for details.

## Design

1. `Chat`: the place where one or more user communicate with agents through channels
2. `Agent`: the agent that do things by LLMs, for now by acps
3. `Channel`: the message comes and goes
4. `Replier`: reponse to the user messages
5. `Command Chian`: handle user commmand messages

a chat may represent 1-1 or group chat on telegram.
a chat have mutiple repliers
a agent replier have a agent behind to it.

the command chain can control chat, the replier, or the global state.
