import { Box, Flex, Link, Text } from "@chakra-ui/react";
import { Link as RouterLink, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { label: "File Upload", path: "/" },
    { label: "Chat", path: "/chat" },
  ];

  return (
    <Box bg="blue.500" px={4} py={3}>
      <Flex maxW="1200px" mx="auto" align="center" justify="space-between">
        <Text fontSize="xl" color="white" fontWeight="bold">
          Document Chat
        </Text>
        <Flex gap={6}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              as={RouterLink}
              to={item.path}
              color="white"
              fontWeight={location.pathname === item.path ? "bold" : "normal"}
              _hover={{ textDecoration: "none", opacity: 0.8 }}
            >
              {item.label}
            </Link>
          ))}
        </Flex>
      </Flex>
    </Box>
  );
};

export default Navbar;
