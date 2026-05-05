// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InitNetworksProjectPost {
    pub project: String,

    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

}