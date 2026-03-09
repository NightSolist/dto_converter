mod client;
mod config;
mod incus;
mod lab;
mod remotes;

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::Path;
use std::fs;

#[derive(Parser)]
#[command(name = "incus-lab")]
#[command(about = "Incus Lab Manager", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Deploy a lab from YAML file
    Deploy {
        #[arg(short, long)]
        file: String,
    },
    /// Destroy a lab defined in YAML file
    Destroy {
        #[arg(short, long)]
        file: String,
    },
    /// Start a specific instance
    Start {
        name: String,
    },
    /// Stop a specific instance (force)
    Stop {
        name: String,
    },
    /// Delete a specific instance
    Delete {
        name: String,
    },
    /// List instances (debug)
    Info,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Инициализация
    let cert = Path::new("certs/client.crt");
    let key = Path::new("certs/client.key");
    let client = client::IncusClient::new("https://127.0.0.1:8443", cert, key)?;

    match &cli.command {
        Commands::Info => {
            println!("📡 Checking connection...");
            let info = client.get_server_info().await?;
            println!("✅ Server Info: {}", info);
        }
        Commands::Deploy { file } => {
            let content = fs::read_to_string(file)?;
            let lab_config: config::Lab = serde_yaml::from_str(&content)?;
            let deployer = lab::Deployer::new(&client);
            deployer.deploy(&lab_config).await?;
        }
        Commands::Destroy { file } => {
            let content = fs::read_to_string(file)?;
            let lab_config: config::Lab = serde_yaml::from_str(&content)?;
            let deployer = lab::Deployer::new(&client);
            deployer.destroy(&lab_config).await?;
        }
        // Исправлено: передаем &name (ссылку)
        Commands::Start { name } => {
            println!("▶️ Starting '{}'...", name);
            client.start_instance(name).await?;
            println!("✅ Instance started.");
        }
        Commands::Stop { name } => {
            println!("⏹️ Stopping '{}'...", name);
            client.stop_instance(name).await?;
            println!("✅ Instance stopped.");
        }
        Commands::Delete { name } => {
            println!("🗑️ Deleting '{}'...", name);
            client.delete_instance(name).await?;
            println!("✅ Instance deleted.");
        }
    }

    Ok(())
}