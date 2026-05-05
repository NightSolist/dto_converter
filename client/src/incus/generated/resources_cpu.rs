// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesCPUSocket;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesCPU {
    pub architecture: String,

    pub sockets: Vec<ResourcesCPUSocket>,

    pub total: u64,

}