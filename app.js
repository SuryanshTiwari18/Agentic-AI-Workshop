import os from "os";
import "dotenv/config"; // 1. Load the environment variables immediately
import { GoogleGenAI } from "@google/genai";
import readline from "readline/promises";

// 2. Use process.env.API_KEY instead of a hardcoded string
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let check = true;

const run = async () => {
    // 3. Start chat - Note: Using gemini-2.0-flash for better stability
    const chat = ai.chats.create({
        model: "gemini-2.5-flash-lite", 
        config: {
            systemInstruction: `
                ROLE: You are an expert teacher.
                RULES:
                1. Explain like the user is 10 years old.
                2. Use analogies from daily life.
                3. Never use jargon without explaining it first.
                4. Always end with a encouraging "Teacher's Note".
                5. If the user asks for code, provide it with simple comments.
            `,
            temperature: 1,
            maxOutputTokens: 1000
        }
    });

    console.log("--- Welcome to AI Teacher Terminal ---");

    while (check) {
        let prompt = await rl.question('\nYou: ');

        try {
            // Send message
            let result = await chat.sendMessage({ message: prompt });
            console.log("\nTeacher: ", result.text);

            let choice = await rl.question('\nDo you want to continue? (1 for Yes / 0 for No): ');
            if (choice !== "1") {
                check = false;
            }
        } catch (error) {
            console.error("❌ API Error:", error.message);
            break;
        }
    }
    rl.close();
}

await run();

rl.on('close', () => {
    console.log('\nGoodbye! Keep learning!');
    process.exit(0);
});