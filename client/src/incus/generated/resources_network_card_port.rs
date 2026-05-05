// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesNetworkCardPortInfiniband;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesNetworkCardPort {
    pub id: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub address: Option<String>,

    pub port: u64,

    pub protocol: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub supportedmodes: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub supportedports: Option<Vec<String>>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub porttype: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub transceivertype: Option<String>,

    pub autonegotiation: bool,

    pub linkdetected: bool,

    #[serde(skip_serializing_if = "Option::is_none")]    pub linkspeed: Option<u64>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub linkduplex: Option<String>,

    pub infiniband: Option<ResourcesNetworkCardPortInfiniband>,

}