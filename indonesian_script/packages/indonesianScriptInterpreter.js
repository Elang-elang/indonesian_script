import { python } from "pythonia";
import fs from "fs";

// import
const isi = await python("./main.py").IndonesianScriptInterpreter;

class IndonesianScriptInterpreter {
    constructor({
        filename = null,
        code = null,
        isModule = false
    }) {
        this.filename = filename;
        this.code = code;
        this.isModule = isModule;
        
        this.interp = null;
    }
    
    async loadFile({filename = null}){
        this.filename = filename;
        try {
            this.code = await fs.readFileSync(this.filename);
        } catch (e) {
            throw new Error(
                `File '${filename}' tidak ditemukan`
            );
        }
        return this;
    }
    loadCode({code = null}){
        this.code = code
        return this;
    }
    async run({
        console = false,
        get_interp = false
    }) {
        if (!this.code) {
            throw new Error(
                "Tidak ada kode untuk dijalankan"
            );
        }
        
        this.interp = await isi(filename, code, isModule);
        this.run(console, get_interp);
    }
}