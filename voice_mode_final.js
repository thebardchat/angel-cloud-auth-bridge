// ANGEL CLOUD - VOICE MODE SERVICE (GEMINI-POWERED)
// Purpose: Provides real-time, voice-based conversational access to the Legacy AI system.
// Model Strategy: Uses cost-efficient Gemini 2.5 Flash-Lite for low-latency response.

const fs = require('fs');
const { spawn } = require('child_process');
const readline = require('readline');
const path = require('path');

// **NEW: Google Gemini SDK Import**
const { GoogleGenAI } = require('@google/genai'); 
require('dotenv').config({ path: path.join(__dirname, '.env') }); 

// **IMPORTANT: API Key Sourced from .env**
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// System Instruction for Voice Mode Identity
const VOICE_PROFILE = `
# VOICE MODE IDENTITY: SHANEBRAIN VOICE ASSISTANT
You are the Voice Assistant interface for Shanebrain, the Legacy AI System. 

**YOUR VOICE MODE PURPOSE:**
- Maintain Shane's direct, solution-focused, and fast communication style.
- Keep answers brief and actionable, suitable for spoken word output.
- Your primary goal is to facilitate quick, hands-free information access and task resolution.
- Only respond with the content required; do not include conversation markers or lengthy preambles.
`;


class VoiceModeFinal {
    constructor() {
        if (!GEMINI_API_KEY) {
            throw new Error("GEMINI_API_KEY not set. Cannot run Voice Mode.");
        }
        
        // **Initialize Google Gemini Client**
        this.ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });
        this.model = "gemini-2.5-flash-lite"; // Cost-efficient and fast
        this.conversationContext = [];
    }

    // Record audio with Windows MCI (Uses the original implementation)
    recordAudio(duration = 5) {
        return new Promise((resolve, reject) => {
            const audioFile = `recording_${Date.now()}.wav`;
            
            const ps = spawn('powershell', [
                '-Command',
                `
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class AudioRecorder {
                    [DllImport("winmm.dll")]
                    public static extern int mciSendString(string command, System.Text.StringBuilder returnValue, int returnLength, IntPtr hwndCallback);
                }
"@
                [AudioRecorder]::mciSendString("open new Type waveaudio Alias recsound", $null, 0, [IntPtr]::Zero)
                [AudioRecorder]::mciSendString("record recsound", $null, 0, [IntPtr]::Zero)
                Start-Sleep -Seconds ${duration}
                [AudioRecorder]::mciSendString("save recsound ${audioFile}", $null, 0, [IntPtr]::Zero)
                [AudioRecorder]::mciSendString("close recsound", $null, 0, [IntPtr]::Zero)
                Write-Output "DONE:${audioFile}"
                `
            ]);

            let output = '';
            ps.stdout.on('data', (data) => {
                output += data.toString();
            });

            ps.on('close', () => {
                const match = output.match(/DONE:(.+)/);
                if (match && fs.existsSync(match[1].trim())) {
                    resolve(match[1].trim());
                } else {
                    reject(new Error('Recording failed or file not found.'));
                }
            });
        });
    }

    // Simple speech-to-text placeholder (Uses keyboard input for accuracy/simplicity)
    async transcribeLocal(audioFile) {
        return new Promise((resolve) => {
            console.log('\n⌨️  Type what you said (or press Enter to use voice recognition):');
            const rl = readline.createInterface({
                input: process.stdin,
                output: process.stdout
            });

            rl.question('> ', (answer) => {
                rl.close();
                // Clean up the recorded file
                if (fs.existsSync(audioFile)) {
                    fs.unlinkSync(audioFile);
                }
                resolve(answer || 'Hello');
            });
        });
    }

    // **NEW: Call Gemini API**
    async callGemini(message) {
        // 1. Add current user message to context (Role MUST be "user")
        this.conversationContext.push({ role: "user", parts: [{ text: message }] });

        // Keep last 10 messages (5 exchanges) for token efficiency in Voice Mode
        const contentsToSend = this.conversationContext.slice(-10);

        try {
            const response = await this.ai.models.generateContent({
                model: this.model,
                contents: contentsToSend,
                config: {
                    systemInstruction: VOICE_PROFILE // Pass the specific Voice Profile
                }
            });
            
            const responseText = response.text;
            
            // Update context with the AI's response (Role MUST be "model")
            this.conversationContext.push({ 
                role: "model", 
                parts: [{ text: responseText }]
            });

            return responseText;

        } catch (error) {
            console.error("Gemini API Error:", error.message);
            return "I'm experiencing a high-level network issue. Please try typing your request instead of speaking, or check the Gemini API key.";
        }
    }

    // Speak response (Uses the original implementation)
    speak(text) {
        return new Promise((resolve) => {
            // NOTE: SpeechSynthesizer rate is set to 1 for a slightly slower, clearer pace.
            const ps = spawn('powershell', [
                '-Command',
                `Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Rate = 1; $speak.Speak('${text.replace(/'/g, "''")}')`
            ]);
            ps.on('close', () => resolve());
        });
    }

    // Main loop - Push to talk
    async start() {
        console.log('======================================================');
        console.log('=== ANGEL CLOUD VOICE MODE ACTIVE (PUSH-TO-TALK) ===');
        console.log(`Model: ${this.model} | Low Cost/High Speed`);
        console.log('======================================================');
        console.log('Press ENTER to start recording, type "quit" to exit\n');

        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        const promptUser = () => {
            rl.question('Press ENTER to speak (or "quit"): ', async (input) => {
                if (input.toLowerCase() === 'quit') {
                    console.log('Voice Mode terminated. Goodbye!');
                    rl.close();
                    process.exit(0);
                }

                try {
                    console.log('\n🎤 Recording 5 seconds...');
                    const audioFile = await this.recordAudio(5);
                    
                    const text = await this.transcribeLocal(audioFile);
                    
                    if (text && text.trim().length > 0) {
                        console.log(`\nYou: ${text}`);
                        
                        const response = await this.callGemini(text);
                        console.log(`\nAngel: ${response}\n`);
                        
                        await this.speak(response);
                    }

                } catch (err) {
                    console.error('Error:', err.message);
                }

                promptUser();
            });
        };

        promptUser();
    }
}

if (require.main === module) {
    try {
        const voice = new VoiceModeFinal();
        voice.start();
    } catch (e) {
        console.error(`\nFatal Error during Voice Mode initialization: ${e.message}\n`);
        console.log("Action Required: Ensure 'GEMINI_API_KEY' is set in your .env file.");
    }
}

module.exports = VoiceModeFinal;