// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLease {
    pub hostname: String,

    pub hwaddr: String,

    pub address: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub location: String,

}