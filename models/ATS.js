const mongoose = require("mongoose");
const { Schema } = mongoose;

// Define the Job Schema
const ATSSchema = new Schema({
  companyName: {
    type: String,
    required: true,
    trim: true,
  },
  jobDescription: {
    type: String,
    required: true,
  },
  user: {
    type: Schema.Types.ObjectId,
    ref: "User", // Reference to the User model
    required: true,
  },
  aiResponse: {
    type: Object, // AI-generated insights or analysis related to the job
    default: {},
  },
  pdfPath: {
    type: String, // Path to the uploaded PDF
    default: null,
  },
  pdfBlob: {
    type: Buffer,
    default: null,
  }
}, { timestamps: true });


// Export the Job model
const ATS = mongoose.model("ATS", ATSSchema);

module.exports = ATS;
