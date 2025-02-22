import { useState } from 'react';
import { Menu, X, LogOut, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NavbarProps {
  isExpanded?: boolean;
}

export function Navbar({ isExpanded = false }: NavbarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(true); // Replace with actual auth state

  const menuItems = [
    { name: 'Dashboard', href: '/' },
    { name: 'Projects', href: '/projects' },
    { name: 'Settings', href: '/settings' },
  ];

  const toggleMenu = () => setIsOpen(!isOpen);

  const handleLogout = () => {
    // Implement logout logic here
    setIsLoggedIn(false);
  };

  return (
    <motion.nav
      initial={{
        backgroundColor: "rgba(17, 24, 39, 0.5)",
        position: "relative",
        width: "50%",
        marginBottom: "2rem",
        borderRadius: "1rem",
      }}
      animate={{
        backgroundColor: isExpanded ? "rgba(17, 24, 39, 0.9)" : "rgba(17, 24, 39, 0.5)",
        position: isExpanded ? "fixed" : "relative",
        top: isExpanded ? 0 : "2rem",
        width: isExpanded ? "100%" : "50%",

        marginBottom: "2rem",
        borderRadius: isExpanded ? 0 : "1rem",
        zIndex: 50,
      }}
      transition={{ 
        duration: 0.8,
        ease: [0.4, 0, 0.2, 1],
        backgroundColor: { duration: 0.3 }
      }}
      className="backdrop-blur-sm border-b border-gray-800"
    >
      <motion.div
        initial={{
          maxWidth: "60rem",
          padding: "0 1rem",
        }}
        animate={{
          maxWidth: isExpanded ? "100%" : "60rem",
          padding: isExpanded ? "0 2rem" : "0 1rem",
        }}
        transition={{ 
          duration: 0.8,
          ease: [0.4, 0, 0.2, 1]
        }}
        className="mx-auto sm:px-6 lg:px-8"
      >
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <div className="flex-shrink-0">
            <a href="/" className="flex items-center">
              <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-400">
                VideoAI
              </span>
            </a>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6">
            {menuItems.map((item) => (
              <motion.a
                key={item.name}
                href={item.href}
                whileHover={{ scale: 1.05 }}
                className="text-gray-300 hover:text-white px-2 py-1 text-sm font-medium transition-colors duration-200"
              >
                {item.name}
              </motion.a>
            ))}
            {isLoggedIn && (
              <div className="flex items-center space-x-4">
                <motion.a
                  href="/profile"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                  title="Profile"
                >
                  <User size={20} />
                </motion.a>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLogout}
                  className="text-gray-300 hover:text-white transition-colors duration-200"
                  title="Logout"
                >
                  <LogOut size={20} />
                </motion.button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-400 hover:text-white focus:outline-none"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-gray-800/50 backdrop-blur-sm"
          >
            <div className="px-2 pt-2 pb-3 space-y-1">
              {menuItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                >
                  {item.name}
                </a>
              ))}
              {isLoggedIn && (
                <>
                  <a
                    href="/profile"
                    className="w-full text-left text-gray-300 hover:text-white flex items-center px-3 py-2 rounded-md text-base font-medium"
                  >
                    <User size={20} className="mr-2" />
                    Profile
                  </a>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left text-gray-300 hover:text-white flex items-center px-3 py-2 rounded-md text-base font-medium"
                  >
                    <LogOut size={20} className="mr-2" />
                    Logout
                  </button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
