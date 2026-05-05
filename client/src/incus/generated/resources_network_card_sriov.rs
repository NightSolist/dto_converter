// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesNetworkCard;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesNetworkCardSRIOV {
    pub currentvfs: u64,

    pub maximumvfs: u64,

    pub vfs: Vec<ResourcesNetworkCard>,

}