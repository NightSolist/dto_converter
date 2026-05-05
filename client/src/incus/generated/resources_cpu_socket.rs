// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesCPUAddressSizes;
use crate::incus::ResourcesCPUCache;
use crate::incus::ResourcesCPUCore;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesCPUSocket {
    #[serde(skip_serializing_if = "Option::is_none")]    pub name: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub vendor: Option<String>,

    pub socket: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub cache: Option<Vec<ResourcesCPUCache>>,

    pub cores: Vec<ResourcesCPUCore>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub frequency: Option<u64>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub frequencyminimum: Option<u64>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub frequencyturbo: Option<u64>,

    pub addresssizes: Option<ResourcesCPUAddressSizes>,

}