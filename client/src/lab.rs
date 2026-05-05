use anyhow::Result;
use std::collections::HashMap;

use crate::client::IncusClient;
use crate::config::{Lab, InstanceConfig, NetworkConfig};
use crate::remotes;

use crate::incus::{InstanceSource, InstanceType, InstancesPost, NetworksPost};

pub struct Deployer<'a> { client: &'a IncusClient }

impl<'a> Deployer<'a> {
    pub fn new(client: &'a IncusClient) -> Self { Self { client } }

    pub async fn deploy(&self, lab: &Lab) -> Result<()> {
        if let Some(desc) = &lab.description {
            println!("🚀 Deploying lab: {} ({})", lab.name, desc);
        } else {
            println!("🚀 Deploying lab: {}", lab.name);
        }

        for net in &lab.networks {
            self.deploy_network(net).await?;
        }

        for instance in &lab.instances {
            self.deploy_instance(instance).await?;
        }

        println!("✅ Lab deployed successfully!");
        Ok(())
    }

    pub async fn destroy(&self, lab: &Lab) -> Result<()> {
        println!("🔥 Destroying lab: {}", lab.name);

        for instance in &lab.instances {
            println!("   🗑️  Deleting instance: {}", instance.name);
            let _ = self.client.delete_instance(&instance.name).await;
        }

        for net in &lab.networks {
            println!("   🗑️  Deleting network: {}", net.name);
            let _ = self.client.delete_network(&net.name).await;
        }

        println!("✅ Lab destroyed.");
        Ok(())
    }

    async fn deploy_network(&self, config: &NetworkConfig) -> Result<()> {
        println!("🌐 Deploying network '{}'", config.name);
        
        let _ = self.client.delete_network(&config.name).await;

        let mut net_config = HashMap::new();
        if let Some(ipv4) = &config.ipv4 {
            net_config.insert("ipv4.address".to_string(), ipv4.clone());
            net_config.insert("ipv4.nat".to_string(), "true".to_string());
        }
        
        if let Some(ipv6) = &config.ipv6 {
            if ipv6 == "none" {
                net_config.insert("ipv6.address".to_string(), "none".to_string());
            } else {
                net_config.insert("ipv6.address".to_string(), ipv6.clone());
                net_config.insert("ipv6.nat".to_string(), "true".to_string());
            }
        } else {
            net_config.insert("ipv6.address".to_string(), "none".to_string());
        }

        if let Some(dns) = &config.dns_domain {
            net_config.insert("dns.domain".to_string(), dns.clone());
        }
        
        let req = NetworksPost {
            name: config.name.clone(),
            r#type: "bridge".to_string(),
            config: net_config,
            ..Default::default()
        };

        self.client.create_network(&req).await?;
        println!("✅ Created network {}", config.name);
        Ok(())
    }

    async fn deploy_instance(&self, config: &InstanceConfig) -> Result<()> {
        println!("📦 Deploying {} ({})", config.name, config.type_);
        let _ = self.client.delete_instance(&config.name).await;
        
        let (server, protocol, alias) = remotes::parse_image(&config.image);
        let type_enum = if config.type_ == "virtual-machine" { InstanceType::InstanceTypeVM } else { InstanceType::InstanceTypeContainer };
        
        let mut devices = HashMap::new();
        if let Some(net_name) = &config.network {
            let mut eth0 = HashMap::new();
            eth0.insert("type".to_string(), "nic".to_string());
            eth0.insert("nictype".to_string(), "bridged".to_string());
            eth0.insert("parent".to_string(), net_name.clone());
            eth0.insert("name".to_string(), "eth0".to_string());
            
            devices.insert("eth0".to_string(), eth0);
        }

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
            devices: devices,
            config: config.config.clone().into_iter().collect(),
            start: config.start,
            ..Default::default()
        };

        self.client.create_instance(&req).await?;
        println!("✅ Created {}", config.name);
        
        Ok(())
    }
}