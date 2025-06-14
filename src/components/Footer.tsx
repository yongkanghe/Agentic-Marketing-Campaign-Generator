/**
 * FILENAME: Footer.tsx
 * DESCRIPTION/PURPOSE: Footer component with attribution, disclaimer, and licensing information
 * Author: JP + 2024-12-19
 */

import React from 'react';
import { MaterialCard } from './MaterialCard';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="container mx-auto px-4 py-8">
        <MaterialCard className="p-6">
          <div className="text-center space-y-4">
            {/* Attribution */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Video Venture Launch - Agentic AI Marketing Campaign Manager
              </h3>
              <p className="text-gray-600">
                Authored by{' '}
                <a 
                  href="https://www.linkedin.com/in/johas" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="font-bold text-blue-600 hover:text-blue-800 underline"
                >
                  Jaroslav Pantsjoha
                </a>{' '}
                for the <strong>Agentic AI Solution Hackathon</strong>
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Powered by Google's Agent Development Kit (ADK) and Gemini AI
              </p>
            </div>

            {/* Disclaimer */}
            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-medium text-gray-700 mb-2">Disclaimer</h4>
              <p className="text-xs text-gray-500 max-w-4xl mx-auto leading-relaxed">
                This software is provided "as is", without warranty of any kind, express or implied, 
                including but not limited to the warranties of merchantability, fitness for a particular 
                purpose and noninfringement. In no event shall the authors or copyright holders be liable 
                for any claim, damages or other liability, whether in an action of contract, tort or 
                otherwise, arising from, out of or in connection with the software or the use or other 
                dealings in the software.
              </p>
            </div>

            {/* License */}
            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-medium text-gray-700 mb-2">License</h4>
              <p className="text-xs text-gray-500 mb-2">
                Licensed under the Apache License, Version 2.0 (the "License")
              </p>
              <div className="text-xs text-gray-400 space-y-1">
                <p>
                  You may not use this file except in compliance with the License. 
                  You may obtain a copy of the License at:
                </p>
                <a 
                  href="http://www.apache.org/licenses/LICENSE-2.0" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  http://www.apache.org/licenses/LICENSE-2.0
                </a>
                <p>
                  Unless required by applicable law or agreed to in writing, software 
                  distributed under the License is distributed on an "AS IS" BASIS, 
                  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
                  See the License for the specific language governing permissions and 
                  limitations under the License.
                </p>
              </div>
            </div>

            {/* Additional Info */}
            <div className="border-t border-gray-200 pt-4">
              <div className="flex flex-wrap justify-center gap-4 text-xs text-gray-400">
                <span>© 2024 Jaroslav Pantsjoha</span>
                <span>•</span>
                <span>Built with React, TypeScript & Google ADK</span>
                <span>•</span>
                <span>MVP Grade Solution</span>
                <span>•</span>
                <a 
                  href="https://github.com/google/adk" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  Google ADK Framework
                </a>
              </div>
            </div>
          </div>
        </MaterialCard>
      </div>
    </footer>
  );
};

export default Footer; 