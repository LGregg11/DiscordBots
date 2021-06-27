using System;

namespace DiscordBotCommon
{
    public class DiscordBot : IDiscordBot
    {
        public virtual string Name => throw new MissingFieldException("No Name");

        public virtual string CommandPrefix => throw new MissingFieldException("No Command Prefix");

        public void Start()
        {
            Console.WriteLine($"{Name} started - command prefix: '{CommandPrefix}'..");
        }

        public void Stop()
        {
            Console.WriteLine($"{Name} stopped..");
        }
    }
}
