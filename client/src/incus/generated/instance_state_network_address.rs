// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceStateNetworkAddress {
    pub family: String,

    pub address: String,

    pub netmask: String,

    pub scope: String,

}