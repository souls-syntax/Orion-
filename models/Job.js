const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Define the Job schema
const jobSchema = new Schema({
  role: {
    type: String,
    required: true, // Ensures this field is mandatory
  },
  company: {
    type: String,
    required: true, // Ensures this field is mandatory
  },
  description: {
    type: String,
    required: false, // Description is optional
  },
  salary: {
    type: String,
    required: false, // Salary is optional
  },
  aiResponse: {
    type: Schema.Types.Mixed, // Stores any kind of object or array
    required: false, // AI response is optional
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User', // Foreign key reference to the User model
    required: true, // This will associate each job with a user
  }
}, {
  timestamps: true, // Automatically adds createdAt and updatedAt fields
});

// Create a Mongoose model from the schema
const Job = mongoose.model('Job', jobSchema);

module.exports = Job;
