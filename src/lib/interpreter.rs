use std::collections::HashMap;
// use pyo3::prelude::*;
// use pyo3::types::PyDict;
// Asumsi: file lib.rs berisi struct Scope dan enum Value yang kita buat sebelumnya

use super::scope::Scope;
use super::variable::Value;

#[derive(Debug, Clone)]
enum Module {
    Str(String),
    Dict(HashMap<String, Module>), // HashMap harus punya tipe Key dan Value
}

pub struct Interpreter {
    pub current_scope: Scope,
    _module: HashMap<String, Module>,
    _infunction: bool,
    _inclass: bool,
    _inloop: bool,
    _inswitch: bool,
    filename: String,
}

impl Interpreter {
    // Rust tidak mendukung default parameter. Kita buat manual atau pakai Option.
    pub fn new(filename: Option<&str>, ismodule: bool) -> Self {
        let f_name = filename.unwrap_or("<is-stdout>");
        
        // Inisialisasi Scope (asumsi lib::Scope::new(None) ada)
        let current_scope = Scope::new(None);
        
        let mut module_map = HashMap::new();
        module_map.insert("ekspor".to_string(), Module::Dict(HashMap::new()));
        module_map.insert("impor".to_string(), Module::Dict(HashMap::new()));
        
        if ismodule {
            module_map.insert("berkas".to_string(), Module::Str("utama".to_string()));
        } else {
            module_map.insert("berkas".to_string(), Module::Str(f_name.to_string()));
        }
        
        Self {
            current_scope,
            _module: module_map,
            _infunction: false,
            _inclass: false,
            _inloop: false,
            _inswitch: false,
            filename: f_name.to_string(),
        }
    }
    
    // Method untuk menggabungkan variabel dari interpreter lain
    pub fn load_interp(&mut self, interp: Interpreter){
        // Kita loop variabel dari interpreter lain
        for (var_name, obj) in &interp.current_scope.vars {
            if !self.current_scope.has(var_name) {
                // Pastikan fungsi declare di lib.rs menerima &str untuk nama
                self.current_scope.declare(
                    var_name,
                    obj.value.clone(),
                    obj.tipe.clone(),
                    Some(obj.address.clone()),
                    obj.constant,
                ).ok(); // Kita abaikan hasilnya atau handle errornya
            }
        }
    }
    
    // pub load(&mut self, node: )
}