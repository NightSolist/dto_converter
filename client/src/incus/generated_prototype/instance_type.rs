// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Default)]
pub enum InstanceType {
    #[default]    #[serde(rename = "")]    InstanceTypeAny,
    #[serde(rename = "container")]    InstanceTypeContainer,
    #[serde(rename = "virtual-machine")]    InstanceTypeVM,
}