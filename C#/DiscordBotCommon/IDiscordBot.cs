using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DiscordBotCommon
{
    public interface IDiscordBot
    {
        string Name { get; }
        string CommandPrefix { get; }
        void Start();
        void Stop();
    }
}
