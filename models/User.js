const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: true
  },
  currentJobRole: {
    type: String,
    trim: true,
    required: true
  },
  currentCompany: {
    type: String,
    trim: true,
    required: true
  },
  jobDescription: {
    type: String,
    trim: true,
    required: true
  }
}, {
  timestamps: true // Automatically creates `createdAt` and `updatedAt` fields
});

const User = mongoose.model('User', userSchema);

module.exports = User;
