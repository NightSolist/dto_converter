// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkStateOVN {
    pub chassis: String,

    pub logicalrouter: String,

    pub logicalswitch: String,

    pub uplinkipv4: String,

    pub uplinkipv6: String,

}