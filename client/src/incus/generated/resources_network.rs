// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesNetworkCard;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesNetwork {
    pub cards: Vec<ResourcesNetworkCard>,

    pub total: u64,

}