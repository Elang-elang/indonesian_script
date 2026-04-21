/**
 * WhatsApp Bridge for Pi - Connection Class (adapted from bot.js)
 * Handles pairing code, auto-retry, and connection lifecycle
 */
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import makeWASocket, {
    DisconnectReason,
    useMultiFileAuthState,
    Browsers,
} from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import pino from "pino";

// ==================== CONSTANTS ====================
const HOME_DIR = os.homedir();
const AUTH_PATH = path.join(HOME_DIR, ".pi", "whatsapp-auth");
const CONFIG_FILE = path.join(HOME_DIR, ".pi", "whatsapp-bridge.json");
const CACHE_DIRS = [
    path.join(HOME_DIR, ".pi", "cache", "Img"),
    path.join(HOME_DIR, ".pi", "cache", "Vid"),
    path.join(HOME_DIR, ".pi", "cache", "Quoted"),
    path.join(HOME_DIR, ".pi", "cache", "ResultAI"),
    path.join(HOME_DIR, ".pi", "cache", "Aud"),
    path.join(HOME_DIR, ".pi", "cache", "Sticker"),
    path.join(HOME_DIR, ".pi", "cache", "ytdlp"),
];

// Logger (silent for production, can be enabled)
const logger = pino({ level: "silent" });

// ==================== INTERFACES ====================
interface WhatsAppBridgeState {
    connected: boolean;
    phoneNumber?: string;
    lastSenderJid?: string | null;
    pairingRequested?: boolean;
    retryCount: number;
}

// ==================== HELPER FUNCTIONS ====================
function safeNotify(ctx: any, message: string, type: "info" | "error" | "success" | "warning" = "info") {
    try {
        if (ctx && ctx.ui && typeof ctx.ui.notify === "function") {
            ctx.ui.notify(message, type);
        } else {
            const prefix = type === "error" ? "❌" : type === "success" ? "✅" : type === "warning" ? "⚠️" : "📱";
            console.log(`\n${prefix} ${message}\n`);
        }
    } catch (e) {
        console.log(`\n📱 ${message}\n`);
    }
}

function printColoredHelp() {
    const colors = {
        reset: "\x1b[0m",
        bright: "\x1b[1m",
        cyan: "\x1b[36m",
        green: "\x1b[32m",
        yellow: "\x1b[33m",
        blue: "\x1b[34m",
        magenta: "\x1b[35m",
        red: "\x1b[31m",
    };
    console.log("\n" + "═".repeat(70));
    console.log(`${colors.bright}${colors.cyan}   📱 WHATSAPP BRIDGE FOR PI - HELP MENU ${colors.reset}`);
    console.log("═".repeat(70));
    console.log(`\n${colors.bright}${colors.yellow}🔌 COMMANDS:${colors.reset}\n`);
    console.log(`${colors.green}/whatsapp-connect +628123456789${colors.reset}      Connect with pairing code`);
    console.log(`${colors.green}/whatsapp-status${colors.reset}                     Check connection status`);
    console.log(`${colors.green}/whatsapp-disconnect${colors.reset}                 Disconnect WhatsApp`);
    console.log(`${colors.green}/whatsapp-reset${colors.reset}                      Reset authentication (logout)`);
    console.log(`${colors.green}/whatsapp-help${colors.reset}                       Show this help menu`);
    console.log(`\n${colors.bright}${colors.yellow}📖 HOW TO CONNECT:${colors.reset}\n`);
    console.log(`${colors.magenta}🔐 PAIRING CODE METHOD:${colors.reset}`);
    console.log(`  1. ${colors.green}/whatsapp-connect +628123456789${colors.reset}`);
    console.log(`  2. Wait for pairing code notification`);
    console.log(`  3. ${colors.bright}Open WhatsApp on your phone${colors.reset}`);
    console.log(`  4. Go to ${colors.yellow}Settings → Linked Devices → Link with Phone Number${colors.reset}`);
    console.log(`  5. ${colors.bright}Enter the 8-digit pairing code shown above${colors.reset}`);
    console.log(`  6. Wait for "✅ WhatsApp Connected Successfully!" message\n`);
    console.log(`${colors.bright}${colors.red}⚠️ TROUBLESHOOTING "Connection Failure":${colors.reset}`);
    console.log(`  • Check your internet connection`);
    console.log(`  • Run ${colors.green}/whatsapp-reset${colors.reset} then try again`);
    console.log(`  • Wait 30 seconds and retry`);
    console.log("═".repeat(70) + "\n");
}

function showPairingInstructions(ctx: any, code: string, phoneNumber: string) {
    const border = "█".repeat(60);
    const emptyLine = "█" + " ".repeat(58) + "█";
    console.log("\n" + border);
    console.log(emptyLine);
    console.log(`█  ${"🔐".repeat(10)}  🔐 WHATSAPP PAIRING REQUIRED 🔐  ${"🔐".repeat(10)}  █`);
    console.log(emptyLine);
    console.log(`█  📱 Phone Number: ${phoneNumber.padEnd(44)} █`);
    console.log(emptyLine);
    console.log(`█  🔑 PAIRING CODE: ${code.padEnd(46)} █`);
    console.log(emptyLine);
    console.log(`█  ⚠️  ACTION REQUIRED:${" ".repeat(43)} █`);
    console.log(emptyLine);
    console.log(`█  1. Open WhatsApp on your PHONE${" ".repeat(33)} █`);
    console.log(`█  2. Go to: Settings → Linked Devices${" ".repeat(26)} █`);
    console.log(`█  3. Tap "Link with Phone Number"${" ".repeat(29)} █`);
    console.log(`█  4. Enter this pairing code: ${code}${" ".repeat(31)} █`);
    console.log(emptyLine);
    console.log(`█  ⏰ This code expires in 2 minutes${" ".repeat(32)} █`);
    console.log(emptyLine);
    console.log(border + "\n");

    const notificationMsg = [
        "🔐 WHATSAPP PAIRING REQUIRED!",
        `Phone: ${phoneNumber}`,
        `Pairing Code: ${code}`,
        "Steps:",
        "1. Open WhatsApp on your phone",
        "2. Settings → Linked Devices → Link with Phone Number",
        "3. Enter the pairing code above",
        "⏰ Code expires in 2 minutes!"
    ].join("\n");
    safeNotify(ctx, notificationMsg, "warning");
}

// ==================== CONNECTION CLASS ====================
class Connection {
    private socket: any = null;
    private state: WhatsAppBridgeState;
    private reconnectTimer: NodeJS.Timeout | null = null;
    private currentRetryTimeout: NodeJS.Timeout | null = null;
    private saveCreds: (() => Promise<void>) | null = null;
    private pi: ExtensionAPI | null = null;
    private ctx: any = null;

    constructor(pi?: ExtensionAPI, ctx?: any) {
        this.pi = pi || null;
        this.ctx = ctx || null;
        this.state = {
            connected: false,
            lastSenderJid: null,
            pairingRequested: false,
            retryCount: 0,
        };
        this.loadState();
        this.ensureDirectories();
    }

    // ========== PRIVATE METHODS (State & Files) ==========
    private loadState(): void {
        try {
            if (fs.existsSync(CONFIG_FILE)) {
                this.state = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
            }
        } catch (e) {
            console.error("Failed to load state:", e);
        }
    }

    private saveState(): void {
        try {
            fs.writeFileSync(CONFIG_FILE, JSON.stringify(this.state, null, 2), { mode: 0o600 });
        } catch (e) {
            console.error("Failed to save state:", e);
        }
    }

    private ensureDirectories(): void {
        try {
            fs.mkdirSync(AUTH_PATH, { recursive: true, mode: 0o700 });
            fs.mkdirSync(path.dirname(CONFIG_FILE), { recursive: true });
            for (const dir of CACHE_DIRS) {
                fs.mkdirSync(dir, { recursive: true });
            }
        } catch (e) {
            console.error("Failed to create directories:", e);
        }
    }

    private resetRetryCount(): void {
        this.state.retryCount = 0;
        this.saveState();
    }

    private getRetryDelay(): number {
        const delays = [5000, 10000, 20000, 40000, 60000];
        const index = Math.min(this.state.retryCount, delays.length - 1);
        return delays[index];
    }

    // ========== CACHE CLEARING (adapted from bot.js _clearCache) ==========
    private async clearCache(): Promise<void> {
        try {
            for (const dir of CACHE_DIRS) {
                try {
                    if (fs.existsSync(dir)) {
                        fs.rmSync(dir, { recursive: true, force: true });
                    }
                    fs.mkdirSync(dir, { recursive: true });
                    console.log(`✓ Cache ${path.basename(dir)} cleared`);
                } catch (err: any) {
                    console.warn(`⚠ Failed to clear ${dir}:`, err.message);
                }
            }
            console.log("✓ All caches cleared");
        } catch (err: any) {
            console.error("✗ Error clearing caches:", err.message);
        }
    }

    // ========== EVENT HANDLERS (adapted from bot.js) ==========
    private async handleConnectionUpdate(update: any): Promise<void> {
        const { connection, lastDisconnect } = update;
        if (connection === "close") {
            await this.handleDisconnection(lastDisconnect);
        } else if (connection === "open") {
            await this.handleSuccessfulConnection();
        }
    }

    private async handleDisconnection(lastDisconnect: any): Promise<void> {
        const statusCode = (lastDisconnect?.error as Boom)?.output?.statusCode;
        const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
        console.log(`🔌 Connection closed: ${lastDisconnect?.error?.message || "Unknown reason"}`);
        console.log(`🔄 Should reconnect: ${shouldReconnect}`);

        if (shouldReconnect) {
            if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
            this.reconnectTimer = setTimeout(() => {
                if (this.state.phoneNumber) {
                    this.connect(this.state.phoneNumber, this.ctx);
                }
            }, 3000);
        } else {
            console.log("❌ Logged out permanently. Run /whatsapp-reset and reconnect.");
            safeNotify(this.ctx, "Logged out. Please reset and reconnect.", "error");
            if (this.socket) this.socket.end();
            this.socket = null;
        }
        this.state.connected = false;
        this.saveState();
    }

    private async handleSuccessfulConnection(): Promise<void> {
        console.log("✅ WhatsApp connected successfully!");
        const botJid = this.socket.user?.id;
        if (botJid && this.pi) {
            // Optional: send a startup message to itself (like bot.js does)
            try {
                await this.socket.sendMessage(botJid, {
                    text: "🤖 WhatsApp Bridge for Pi is now active and ready!",
                });
            } catch (e) {
                // ignore
            }
        }
        this.state.connected = true;
        this.state.pairingRequested = false;
        this.resetRetryCount();
        if (this.currentRetryTimeout) {
            clearTimeout(this.currentRetryTimeout);
            this.currentRetryTimeout = null;
        }
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        // Extract phone number from socket user id if available
        if (this.socket.user?.id) {
            const match = this.socket.user.id.match(/(\d+):/);
            if (match) this.state.phoneNumber = match[1];
        }
        this.saveState();

        // Visual success banner
        console.log("\n" + "█".repeat(60));
        console.log("█  ✅✅✅ WHATSAPP CONNECTED SUCCESSFULLY! ✅✅✅  █");
        console.log(`█  📱 Connected as: ${this.state.phoneNumber || "unknown".padEnd(42)} █`);
        console.log("█  💬 Ready to receive and reply to messages              █");
        console.log("█  🎉 You can now chat with Pi through WhatsApp! 🎉      █");
        console.log("█".repeat(60) + "\n");
        safeNotify(this.ctx, "WhatsApp Connected Successfully! Ready to chat.", "success");
    }

    // ========== MAIN CONNECT METHOD (adapted from bot.js connect + pairing) ==========
    public async connect(phoneNumberArg: string, ctx?: any, isRetry: boolean = false): Promise<void> {
        // Prevent multiple connections
        if (this.socket) {
            safeNotify(ctx, "Already connected or connecting!", "warning");
            return;
        }

        // Validate and clean phone number
        let cleanNumber = phoneNumberArg.replace(/[^0-9+]/g, "");
        if (!cleanNumber.startsWith("+")) cleanNumber = "+" + cleanNumber;
        if (!cleanNumber.match(/^\+\d{10,15}$/)) {
            safeNotify(ctx, `Invalid phone number: ${phoneNumberArg}\nUse format: +628123456789`, "error");
            return;
        }

        if (!isRetry) this.resetRetryCount();

        try {
            if (!isRetry) {
                safeNotify(ctx, `Initializing WhatsApp connection for ${cleanNumber}...`, "info");
            } else {
                console.log(`\n🔄 Retry attempt #${this.state.retryCount + 1} for ${cleanNumber}...\n`);
                safeNotify(ctx, `Retry attempt #${this.state.retryCount + 1}...`, "info");
            }

            // Clear cache before connecting (like bot.js does)
            await this.clearCache();

            // Load auth state
            const { state: authState, saveCreds } = await useMultiFileAuthState(AUTH_PATH);
            this.saveCreds = saveCreds;

            // Create socket with Browsers.ubuntu (same as bot.js)
            this.socket = makeWASocket({
                logger,
                printQRInTerminal: false,
                browser: Browsers.ubuntu("Chrome"),
                auth: authState,
                connectTimeoutMs: 30000,
                defaultQueryTimeoutMs: 30000,
                keepAliveIntervalMs: 30000,
            });

            // Set up event listeners
            this.socket.ev.on("creds.update", async () => {
                if (this.saveCreds) await this.saveCreds();
            });
            this.socket.ev.on("connection.update", (update: any) => this.handleConnectionUpdate(update));

            // Variables to track pairing flow
            let pairingRequested = false;
            let pairingCodeReceived = false;
            let connectionFailed = false;

            // Listen for pairing code from socket (automatic)
            this.socket.ev.on("connection.update", async (update: any) => {
                const { pairingCode } = update;
                if (pairingCode && !pairingCodeReceived) {
                    pairingCodeReceived = true;
                    showPairingInstructions(ctx, pairingCode, cleanNumber);
                    this.state.pairingRequested = true;
                    this.saveState();
                }
            });

            // Manually request pairing code after socket is ready
            const waitForReady = setInterval(async () => {
                if (this.socket?.authState?.creds?.registered === false && !pairingRequested && !connectionFailed) {
                    clearInterval(waitForReady);
                    pairingRequested = true;
                    console.log("\n📱 Requesting pairing code from WhatsApp servers...\n");
                    safeNotify(ctx, "Requesting pairing code... Please wait.", "info");
                    try {
                        const code = await this.socket.requestPairingCode(cleanNumber);
                        showPairingInstructions(ctx, code, cleanNumber);
                        this.state.pairingRequested = true;
                        this.saveState();
                    } catch (err: any) {
                        console.log(`\n❌ Failed to get pairing code: ${err.message}\n`);
                        safeNotify(ctx, `Failed to get pairing code: ${err.message}`, "error");
                    }
                }
            }, 1000);

            // Timeout after 30 seconds
            setTimeout(() => {
                clearInterval(waitForReady);
                if (!pairingRequested && !connectionFailed) {
                    console.log("\n⏰ Timeout: Failed to get pairing code. Please try again.\n");
                    safeNotify(ctx, "Timeout: Failed to get pairing code. Check connection and try again.", "error");
                }
            }, 30000);

            // Handle connection errors with exponential backoff (retry logic)
            this.socket.ev.on("connection.update", (update: any) => {
                const { lastDisconnect } = update;
                if (lastDisconnect?.error && !connectionFailed) {
                    const error = lastDisconnect.error;
                    const errorMessage = error.message || "Unknown error";
                    const isConnFailure = errorMessage.includes("Connection Failure") ||
                                          errorMessage.includes("ECONNREFUSED") ||
                                          errorMessage.includes("ETIMEDOUT");
                    if (isConnFailure) {
                        connectionFailed = true;
                        console.log(`\n⚠️ Connection error detected: ${errorMessage}\n`);
                        this.state.retryCount++;
                        this.saveState();
                        const delay = this.getRetryDelay();
                        const maxRetries = 5;
                        if (this.state.retryCount <= maxRetries) {
                            console.log(`\n🔄 Will retry in ${delay / 1000}s (Attempt ${this.state.retryCount}/${maxRetries})\n`);
                            safeNotify(ctx, `Connection failed. Retrying in ${delay / 1000}s...`, "warning");
                            if (this.currentRetryTimeout) clearTimeout(this.currentRetryTimeout);
                            this.currentRetryTimeout = setTimeout(() => {
                                this.socket = null;
                                this.connect(cleanNumber, ctx, true);
                            }, delay);
                        } else {
                            console.log(`\n❌ Max retries (${maxRetries}) reached.\n`);
                            const msg = "❌ CONNECTION FAILED AFTER MULTIPLE RETRIES\nCheck internet/WhatsApp blocking.\nRun /whatsapp-reset and try again.";
                            safeNotify(ctx, msg, "error");
                            this.state.retryCount = 0;
                            this.saveState();
                            this.socket = null;
                        }
                    }
                }
            });

        } catch (error: any) {
            console.error("Connection error:", error);
            safeNotify(ctx, `Connection error: ${error.message}`, "error");
            this.socket = null;
            this.state.connected = false;
            this.saveState();
        }
    }

    // ========== PUBLIC METHODS FOR COMMANDS ==========
    public getSocket() {
        return this.socket;
    }

    public getState() {
        return this.state;
    }

    public updateLastSenderJid(jid: string) {
        this.state.lastSenderJid = jid;
        this.saveState();
    }

    public disconnect(): void {
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
        if (this.currentRetryTimeout) clearTimeout(this.currentRetryTimeout);
        if (this.socket) {
            try {
                this.socket.end();
            } catch (e) {}
            this.socket = null;
        }
        this.state.connected = false;
        this.state.lastSenderJid = null;
        this.state.pairingRequested = false;
        this.state.retryCount = 0;
        this.saveState();
        console.log("\n👋 WhatsApp disconnected\n");
    }

    public async reset(): Promise<void> {
        this.disconnect();
        try {
            if (fs.existsSync(AUTH_PATH)) {
                const files = fs.readdirSync(AUTH_PATH);
                for (const file of files) {
                    fs.unlinkSync(path.join(AUTH_PATH, file));
                }
                fs.rmdirSync(AUTH_PATH);
            }
            this.state = {
                connected: false,
                lastSenderJid: null,
                pairingRequested: false,
                retryCount: 0,
            };
            this.saveState();
            fs.mkdirSync(AUTH_PATH, { recursive: true });
            console.log("\n🔄 WhatsApp authentication reset complete\n");
            safeNotify(this.ctx, "Authentication reset. Use /whatsapp-connect +628123456789 to reconnect", "success");
        } catch (err: any) {
            console.error("Reset error:", err);
            safeNotify(this.ctx, `Reset error: ${err.message}`, "error");
        }
    }
}

// ==================== PI EXTENSION EXPORT ====================
export default function(pi: ExtensionAPI) {
    let connection: Connection | null = null;

    // Initialize connection on first command or lazily
    function getConnection(ctx?: any): Connection {
        if (!connection) {
            connection = new Connection(pi, ctx);
        }
        return connection;
    }

    // Register commands
    pi.registerCommand("whatsapp-connect", {
        description: "Connect WhatsApp using pairing code",
        usage: "/whatsapp-connect +628123456789",
        handler: async (args, ctx) => {
            const trimmed = args.trim();
            const conn = getConnection(ctx);
            if (conn.getState().connected && conn.getSocket()) {
                safeNotify(ctx, "Already connected! Use /whatsapp-status to check", "info");
                return;
            }
            if (conn.getSocket()) {
                safeNotify(ctx, "Connection in progress, please wait...", "warning");
                return;
            }
            if (trimmed === "") {
                safeNotify(ctx, "❌ Phone number required!\nUsage: /whatsapp-connect +628123456789", "error");
                return;
            }
            const phoneRegex = /^\+?[0-9]{10,15}$/;
            let clean = trimmed.replace(/[^0-9+]/g, "");
            if (!clean.startsWith("+")) clean = "+" + clean;
            if (!phoneRegex.test(clean)) {
                safeNotify(ctx, `Invalid phone number: ${trimmed}\nUse format: +628123456789`, "error");
                return;
            }
            safeNotify(ctx, `🔐 Starting WhatsApp pairing for ${clean}...`, "info");
            await conn.connect(clean, ctx);
        },
    });

    pi.registerCommand("whatsapp-status", {
        description: "Check WhatsApp connection status",
        handler: async (_args, ctx) => {
            const conn = getConnection(ctx);
            const state = conn.getState();
            const status = state.connected ? "✅ Connected" : "❌ Disconnected";
            const phone = state.phoneNumber ? `📞 Number: ${state.phoneNumber}` : "";
            const waiting = state.pairingRequested ? "🔐 Waiting for pairing confirmation..." : "";
            const retry = state.retryCount > 0 ? `🔄 Retry attempts: ${state.retryCount}/5` : "";
            console.log("\n" + "─".repeat(50));
            console.log("📱 WHATSAPP BRIDGE STATUS");
            console.log("─".repeat(50));
            console.log(`Status: ${status}`);
            if (phone) console.log(phone);
            if (waiting) console.log(waiting);
            if (retry) console.log(retry);
            if (!state.connected && !conn.getSocket()) {
                console.log("\n📱 To connect, run: /whatsapp-connect +628123456789");
            }
            console.log("─".repeat(50) + "\n");
            safeNotify(ctx, `Status: ${status}`, "info");
        },
    });

    pi.registerCommand("whatsapp-disconnect", {
        description: "Disconnect WhatsApp gracefully",
        handler: async (_args, ctx) => {
            const conn = getConnection(ctx);
            conn.disconnect();
            safeNotify(ctx, "WhatsApp disconnected", "success");
        },
    });

    pi.registerCommand("whatsapp-reset", {
        description: "Reset WhatsApp authentication (clear session)",
        handler: async (_args, ctx) => {
            const conn = getConnection(ctx);
            await conn.reset();
        },
    });

    pi.registerCommand("whatsapp-help", {
        description: "Show help menu",
        handler: async (_args, ctx) => {
            printColoredHelp();
            safeNotify(ctx, "Help menu printed to terminal above", "info");
        },
    });

    // ========== MESSAGE FORWARDING (turn_end) ==========
    pi.on("turn_end", async (event) => {
        if (!connection) return;
        const state = connection.getState();
        const socket = connection.getSocket();
        if (!state.connected || !socket || !state.lastSenderJid) return;

        const message = event.message;
        if (message?.role === "assistant" && message.content) {
            let text = "";
            for (const content of message.content) {
                if (content.type === "text") text += content.text + "\n";
            }
            text = text.trim();
            if (text && state.lastSenderJid) {
                try {
                    await socket.sendMessage(state.lastSenderJid, { text });
                    console.log(`📤 Reply sent to: ${state.lastSenderJid}`);
                } catch (e) {
                    console.error("Failed to send WhatsApp message:", e);
                }
            }
        }
    });

    // Auto-reconnect on Pi startup if previously connected
    setTimeout(async () => {
        if (connection && connection.getState().connected && !connection.getSocket()) {
            const phone = connection.getState().phoneNumber;
            if (phone) {
                console.log("🔄 Auto-reconnecting WhatsApp...");
                await connection.connect(phone, undefined);
            }
        }
    }, 5000);
}