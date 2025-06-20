/* This is a simple Node.js application that provides a RESTful API for generating numerological predictions based on user data.
It is developed with the help of following reference links and libraries:
- Express.js (https://expressjs.com/)
- Mongoose (https://mongoosejs.com/)
- Google Generative AI Node.js SDK (https://www.npmjs.com/package/@google/generative-ai)
- dotenv (https://www.npmjs.com/package/dotenv)
- body-parser (https://www.npmjs.com/package/body-parser)
- cors (https://www.npmjs.com/package/cors)
- Credit to github copilot and VS Code intellisense for assisting in development of this code
*/

// Library imports
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();
const connectionString = process.env.CONNECTION_STRING;
const cors = require('cors');

// Inintializing Express app

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());

// Connecting to MongoDB
if (!connectionString) {
    throw new Error('Connection string is not defined in environment variables.');
}
mongoose.connect(connectionString, { useNewUrlParser: true, useUnifiedTopology: true });

// User Schema
const userSchema = new mongoose.Schema({
    name: String,
    dob: Date,
    email: String,
});

const User = mongoose.model('User', userSchema);

// GeminiFlash 1.5 setup
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

app.post('/api/users', async (req, res) => {
    try {
        const { name, dob, email } = req.body;
        const user = new User({ name, dob, email });
        await user.save();
        const prompt = `Act as a numerologist. The user's name is ${user.name}, and date of birth is ${user.dob.toISOString().slice(0,10)}.  Give a generic numerology prediction. Please format the response in a friendly and engaging manner. Alignments and line spacings for each calculations.`;
        const result = await model.generateContent(prompt);
        res.json({ prediction: result.response.text() });
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Start server 
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Numerology API running on port ${PORT}`));