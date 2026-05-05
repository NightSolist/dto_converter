// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceExecPost {
    pub command: Vec<String>,

    pub waitforws: bool,

    pub interactive: bool,

    pub environment: HashMap<String, String>,

    pub width: i64,

    pub height: i64,

    pub recordoutput: bool,

    pub user: u32,

    pub group: u32,

    pub cwd: String,

}