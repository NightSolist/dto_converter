// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesGPUCard;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesGPU {
    pub cards: Vec<ResourcesGPUCard>,

    pub total: u64,

}