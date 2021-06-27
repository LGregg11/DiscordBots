using DiscordBotCommon;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;

namespace DiscordBots
{
    class Program
    {
        private const string PARENT_DISCORD_BOT_CLASS = "DiscordBot";

        static public List<IDiscordBot> DiscordBots;

        static void Main(string[] args)
        {
            // TODO: Need to check that if two bots have the same command prefix - if so, don't allow the console to run and return an error message
            DiscordBots = new List<IDiscordBot>();

            try
            {
                LoadBotsFromManifestFile();
                CheckCommandPrefixes();
                GetDiscordBots();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
                Environment.Exit(1);
            }
            
            StartBots();

            Console.WriteLine("Press Enter to stop..");
            Console.ReadLine();

            StopBots();
        }

        static void LoadBotsFromManifestFile()
        {
            ICollection<string> botFiles;

            // Read manifest file to create a collection of all the discord bots to be started
            try
            {
                botFiles = File.ReadLines(Directory.GetFiles(Directory.GetCurrentDirectory(), "*.manifest").FirstOrDefault()).ToList();
            }
            catch
            {
                throw new Exception("Could not read manifest file");
            }

            // Attempt to load all bot assemblies, and ouytput a warning for all assemblies that could not be loaded
            foreach (string botFile in botFiles)
            {
                try
                {
                    Assembly.LoadFile(Path.GetFullPath(botFile));
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"WARNING: Couldn't load {botFile} - {ex.Message}");
                }
            }
        }

        static void GetDiscordBots()
        {
            // Find classes in assemblies that hold the DiscordBot interface type
            Type interfaceType = typeof(IDiscordBot);
            Type[] types = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a => a.GetTypes())
                .Where(p => interfaceType.IsAssignableFrom(p) && p.IsClass && p.Name != PARENT_DISCORD_BOT_CLASS)
                .ToArray();

            // Create an instance of the found DiscordBots and add them to a list.
            foreach (Type type in types)
            {
                DiscordBots.Add((IDiscordBot)Activator.CreateInstance(type));
            }
        }

        static void CheckCommandPrefixes()
        {
            // If less than 2 bots, there is no chance of a conflict in command prefixes
            if (DiscordBots.Count < 2)
                return;

            // Create a temporary dictionary to remove 
            IDictionary<string, string> tempDiscordBots = new Dictionary<string, string>();
            DiscordBots.ForEach(b => tempDiscordBots.Add(b.Name, b.CommandPrefix));

            List<string> errors = new List<string>();
            List<string> prefixesAlreadyChecked = new List<string>();
            foreach (string commandPrefix in tempDiscordBots.Values)
            {
                // Ignore cases already checked
                if (prefixesAlreadyChecked.Contains(commandPrefix))
                    continue;

                // Add command prefix to a list to avoid duplicate error messages, and find all matching command prefixes
                prefixesAlreadyChecked.Add(commandPrefix);
                IDictionary<string, string> matchingCommandPrefixes = new Dictionary<string, string>(
                    (IDictionary<string, string>)tempDiscordBots
                    .Where(c => c.Value == commandPrefix));

                // Report an error if there are matching command prefixes
                if (matchingCommandPrefixes.Count() > 1)
                {
                    errors.Add($"'{commandPrefix}' command prefix shared by: {String.Join(", ", matchingCommandPrefixes.Keys.ToList())}");
                }
            }

            // If any errors, throw an exception
            if (errors.Count > 0)
            {
                errors.ForEach(e => Console.WriteLine(e));
                throw new AmbiguousMatchException($"ERROR - Bots with matching command prefixes.\n{String.Join("\n", errors)}");
            }
        }

        static void StartBots()
        {
            foreach (IDiscordBot discordBot in DiscordBots)
            {
                discordBot.Start();
            }
        }
        
        static void StopBots()
        {
            foreach (IDiscordBot discordBot in DiscordBots)
            {
                discordBot.Stop();
            }
        }
}
}
