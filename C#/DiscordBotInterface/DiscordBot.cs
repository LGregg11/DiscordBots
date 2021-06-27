using System;

namespace DiscordBotInterface
{
    public class DiscordBot : IDiscordBot
    {
        public DiscordBot()
        {

        }

        public string Name { get; set => throw new MissingFieldException("No Name") }

        public string CommandPrefix { get; set => throw new MissingFieldException("No CommandPrefix") }

        public void Start()
        {

        }

        public void Stop()
        {

        }

    }
}
