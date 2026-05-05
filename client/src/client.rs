use anyhow::{Context, Result, bail};
use reqwest::{Client, Identity};
use serde_json::Value;
use std::fs;
use std::path::Path;

use crate::incus::{InstancesPost, InstanceStatePut, NetworksPost};

pub struct IncusClient {
    http: Client,
    base_url: String,
}

impl IncusClient {
    pub fn new(base_url: &str, cert_path: &Path, key_path: &Path) -> Result<Self> {
        let cert_pem = fs::read(cert_path).context("Failed to read client.crt")?;
        let key_pem = fs::read(key_path).context("Failed to read client.key")?;
        
        let mut combined_pem = cert_pem;
        combined_pem.push(0x0A);
        combined_pem.extend_from_slice(&key_pem);
        
        let identity = Identity::from_pem(&combined_pem)?;

        let client = Client::builder()
            .identity(identity)
            .danger_accept_invalid_certs(true)
            .build()?;
            
        Ok(Self { http: client, base_url: base_url.to_string() })
    }

    pub async fn get_server_info(&self) -> Result<String> {
        let url = format!("{}/1.0", self.base_url);
        Ok(self.http.get(&url).send().await?.text().await?)
    }

    async fn wait_for_operation(&self, resp: reqwest::Response) -> Result<()> {
        if !resp.status().is_success() { bail!("Request failed: {:?}", resp.text().await?); }
        
        let body: Value = resp.json().await?;
        if body["type"] == "sync" { return Ok(()); }
        
        let id = body["metadata"]["id"].as_str().context("No op ID")?;
        let url = format!("{}/1.0/operations/{}/wait", self.base_url, id);
        
        let w_resp = self.http.get(&url).send().await?;
        let w_body: Value = w_resp.json().await?;
        
        if w_body["metadata"]["status"] == "Success" { 
            Ok(()) 
        } else { 
            bail!("Op failed: {:?}", w_body) 
        }
    }

    // --- INSTANCES ---

    pub async fn create_instance(&self, req: &InstancesPost) -> Result<()> {
        let url = format!("{}/1.0/instances", self.base_url);
        let resp = self.http.post(&url).json(req).send().await?;
        self.wait_for_operation(resp).await
    }

    pub async fn start_instance(&self, name: &str) -> Result<()> {
        let url = format!("{}/1.0/instances/{}/state", self.base_url, name);
        let req = InstanceStatePut { action: "start".to_string(), timeout: -1, force: false, stateful: false };
        let resp = self.http.put(&url).json(&req).send().await?;
        self.wait_for_operation(resp).await
    }

    pub async fn stop_instance(&self, name: &str) -> Result<()> {
        let url = format!("{}/1.0/instances/{}/state", self.base_url, name);
        let req = InstanceStatePut { action: "stop".to_string(), timeout: -1, force: true, stateful: false };
        let resp = self.http.put(&url).json(&req).send().await?;
        self.wait_for_operation(resp).await
    }

    pub async fn delete_instance(&self, name: &str) -> Result<()> {
        let _ = self.stop_instance(name).await;
        let url = format!("{}/1.0/instances/{}", self.base_url, name);
        let resp = self.http.delete(&url).send().await?;
        self.wait_for_operation(resp).await
    }

    // --- NETWORKS ---

    pub async fn create_network(&self, req: &NetworksPost) -> Result<()> {
        let url = format!("{}/1.0/networks", self.base_url);
        let resp = self.http.post(&url).json(req).send().await?;
        self.wait_for_operation(resp).await
    }

    pub async fn delete_network(&self, name: &str) -> Result<()> {
        let url = format!("{}/1.0/networks/{}", self.base_url, name);
        let resp = self.http.delete(&url).send().await?;
        self.wait_for_operation(resp).await
    }
}