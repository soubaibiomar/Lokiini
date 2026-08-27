import React, { useState, useEffect, useRef } from 'react';
import { X, Send, User, MessageSquare, Clock, CheckCheck } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

export default function MessagingDrawer({ isOpen, onClose, currentUser }) {
  const [conversations, setConversations] = useState([
    {
      id: 'c1111111-1111-1111-1111-111111111111',
      dernier_message: 'Bonjour, le perforateur est prêt pour le retrait demain à 9h à Ain Sebaa.',
      non_lus_count: 1,
      autre_participant: { nom: 'Karim Tazi', avatar: null },
      dernier_message_le: new Date().toISOString()
    }
  ]);
  const [activeConvId, setActiveConvId] = useState('c1111111-1111-1111-1111-111111111111');
  const [messages, setMessages] = useState([
    {
      id: 'm1',
      expediteur_id: 'a2222222-2222-2222-2222-222222222222',
      contenu: 'Bonjour, est-ce que les 4 burins SDS-Max sont bien inclus dans le coffret ?',
      cree_le: new Date(Date.now() - 3600000).toISOString(),
      lu: true
    },
    {
      id: 'm2',
      expediteur_id: currentUser?.id || 'a1111111-1111-1111-1111-111111111111',
      contenu: 'Oui absolument, les 2 burins pointus et 2 plats sont fournis et affûtés.',
      cree_le: new Date(Date.now() - 1800000).toISOString(),
      lu: true
    },
    {
      id: 'm3',
      expediteur_id: 'a2222222-2222-2222-2222-222222222222',
      contenu: 'Parfait, je prépare les 240 MAD et la caution cash de 1000 MAD pour demain.',
      cree_le: new Date().toISOString(),
      lu: false
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMsg = {
      id: `m-${Date.now()}`,
      expediteur_id: currentUser?.id || 'a1111111-1111-1111-1111-111111111111',
      contenu: inputMessage.trim(),
      cree_le: new Date().toISOString(),
      lu: true
    };

    setMessages(prev => [...prev, newMsg]);
    setInputMessage('');
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end">
      <div className="bg-white w-full max-w-md h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        
        {/* Drawer Header */}
        <div className="p-4 border-b border-stone-200 flex items-center justify-between bg-stone-50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-stone-900 text-sm">Messagerie Instantanée</h3>
              <span className="text-[11px] text-stone-500">Échanges sécurisés loueur et locataire</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-200 hover:bg-stone-300 flex items-center justify-center text-stone-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Active Contact Bar */}
        <div className="px-4 py-3 border-b border-stone-100 flex items-center justify-between bg-white">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
              <User className="w-4 h-4" />
            </div>
            <div>
              <div className="font-bold text-xs text-stone-900">Karim Tazi</div>
              <div className="text-[10px] text-stone-400">En ligne | Réservation active</div>
            </div>
          </div>
        </div>

        {/* Messages Stream */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-stone-50/50 text-xs">
          {messages.map((m) => {
            const isMe = m.expediteur_id === (currentUser?.id || 'a1111111-1111-1111-1111-111111111111');
            return (
              <div
                key={m.id}
                className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-2xl ${
                    isMe
                      ? 'bg-emerald-800 text-white rounded-br-none'
                      : 'bg-white text-stone-800 border border-stone-200 rounded-bl-none shadow-xs'
                  }`}
                >
                  <p className="leading-relaxed">{m.contenu}</p>
                </div>
                <div className="flex items-center gap-1 text-[10px] text-stone-400 mt-1 px-1">
                  <span>{new Date(m.cree_le).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  {isMe && <CheckCheck className="w-3 h-3 text-emerald-600" />}
                </div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input Bar */}
        <form onSubmit={handleSendMessage} className="p-3 border-t border-stone-200 bg-white flex items-center gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Écrivez votre message..."
            className="flex-1 bg-stone-50 border border-stone-200 rounded-xl px-3.5 py-2.5 text-xs text-stone-900 focus:outline-none focus:border-emerald-800 focus:bg-white transition-all"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim()}
            className="p-2.5 bg-emerald-800 hover:bg-emerald-900 disabled:opacity-40 text-white rounded-xl transition-all shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

      </div>
    </div>
  );
}
