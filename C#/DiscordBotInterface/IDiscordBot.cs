namespace DiscordBotInterface
{
    public interface IDiscordBot
    {
        string Name { get; set; }
        string CommandPrefix { get; set; }
        void Start();
        void Stop();
    }
}
