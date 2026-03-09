use anyhow::Result;
use crate::client::IncusClient;
use crate::config::{Lab, InstanceConfig};
use crate::incus::instancespost::InstancesPost;
use crate::incus::instancesource::InstanceSource;
use crate::incus::instancetype::InstanceType;
use crate::remotes;

pub struct Deployer<'a> { client: &'a IncusClient }

impl<'a> Deployer<'a> {
    pub fn new(client: &'a IncusClient) -> Self { Self { client } }

    pub async fn deploy(&self, lab: &Lab) -> Result<()> {
        println!("🚀 Deploying lab: {}", lab.name);
        for instance in &lab.instances { self.deploy_instance(instance).await?; }
        println!("✅ Lab deployed successfully!");
        Ok(())
    }

    pub async fn destroy(&self, lab: &Lab) -> Result<()> {
        println!("🔥 Destroying lab: {}", lab.name);
        for instance in &lab.instances {
            println!("   🗑️  Deleting instance: {}", instance.name);
            let _ = self.client.delete_instance(&instance.name).await;
        }
        println!("✅ Lab destroyed.");
        Ok(())
    }

    async fn deploy_instance(&self, config: &InstanceConfig) -> Result<()> {
        println!("📦 Deploying {} ({})", config.name, config.type_);
        let _ = self.client.delete_instance(&config.name).await;
        
        let (server, protocol, alias) = remotes::parse_image(&config.image);
        let type_enum = if config.type_ == "virtual-machine" { InstanceType::InstanceTypeVM } else { InstanceType::InstanceTypeContainer };
        
        let req = InstancesPost {
            name: config.name.clone(),
            r#type: type_enum,
            source: InstanceSource {
                r#type: "image".to_string(),
                mode: Some("pull".to_string()),
                server: Some(server),
                protocol: Some(protocol),
                alias: Some(alias),
                ..Default::default()
            },
            profiles: if config.profiles.is_empty() { vec!["default".to_string()] } else { config.profiles.clone() },
            config: config.config.clone().into_iter().collect(),
            start: config.start,
            ..Default::default()
        };

        self.client.create_instance(&req).await?;
        println!("✅ Created {}", config.name);
        
        if config.start { 
            println!("▶️ Starting {}...", config.name);
            self.client.start_instance(&config.name).await?; 
        }
        
        Ok(())
    }
}