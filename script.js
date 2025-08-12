const micButton = document.getElementById('mic-button');
const aiCharacter = document.getElementById('ai-character');
const responseBox = document.getElementById('response');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'en-US';
recognition.interimResults = false;

const synth = window.speechSynthesis;
let speaking = false;

// Ensure voices are ready
speechSynthesis.onvoiceschanged = () => {};

micButton.addEventListener('click', () => {
  recognition.start();
  aiCharacter.classList.remove('idle');
  aiCharacter.classList.add('talking');
});

recognition.onresult = async function (event) {
  const transcript = event.results[0][0].transcript.toLowerCase();
  responseBox.textContent = "You said: " + transcript;
  await respond(transcript);
};

recognition.onend = function () {
  if (!speaking) {
    aiCharacter.classList.remove('talking');
    aiCharacter.classList.add('idle');
  }
};

async function respond(text) {
  if (text.includes("draw")) {
    const query = text.replace("draw", "").trim();
    speak("Here’s a drawing of " + query);
    window.open(`https://www.google.com/search?q=${encodeURIComponent(query)}&tbm=isch`, '_blank');
    return;
  }

  if (text.includes("buy")) {
    speak("Here’s a trusted shopping site for you.");
    window.open("https://www.amazon.in", "_blank");
    return;
  }

  if (text.includes("learn python") || text.includes("work on python")) {
    speak("Try this Python tutorial.");
    window.open("https://www.w3schools.com/python/", "_blank");
    return;
  }

  if (text.includes("thank you") || text.includes("bye")) {
    speak("Thank you!");
    return;
  }

  const geminiReply = await fetchGeminiReply(text);
  speak(geminiReply);
}

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.pitch = 1.2;
  utterance.rate = 1;

  const voices = speechSynthesis.getVoices();
  const femaleVoice = voices.find(v => v.name.toLowerCase().includes("female")) || voices[0];
  utterance.voice = femaleVoice;

  speaking = true;

  utterance.onend = () => {
    speaking = false;
    aiCharacter.classList.remove('talking');
    aiCharacter.classList.add('idle');
  };

  speechSynthesis.speak(utterance);
  responseBox.textContent = "AI: " + text;
}

async function fetchGeminiReply(prompt) {
  const API_KEY = "YOUR_GEMINI_API_KEY"; // Replace with your real Gemini API key

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${API_KEY}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }]
      })
    }
  );

  const data = await response.json();
  try {
    return data.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, I didn't understand that.";
  } catch (e) {
    return "Sorry, there was a problem understanding you.";
  }
}
