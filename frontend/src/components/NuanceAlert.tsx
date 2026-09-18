import React from 'react';
import { Alert, List, Text, Title } from '@mantine/core';
import { IconAlertTriangle } from '@tabler/icons-react';

interface Props {
  caveats: string[];
}

/**
 * Nuance Caveats Sentinel.
 *
 * Surfaces the edge cases, boundary conditions and counter-evidence that a
 * summariser would otherwise silently drop — the primary ethical safeguard
 * against the "cognitive flattening" paradox.
 */
export const NuanceAlert: React.FC<Props> = ({ caveats }) => {
  if (!caveats || caveats.length === 0) return null;

  return (
    <Alert
      color="orange"
      variant="light"
      radius="md"
      icon={<IconAlertTriangle size={18} />}
      title={
        <Title order={5} size="h6">
          Nuance sentinel — do not skip before an exam
        </Title>
      }
    >
      <Text size="xs" mb="xs">
        The original text contains qualifications, boundary conditions or counter-evidence.
        These are exam-critical and are deliberately not simplified away:
      </Text>
      <List size="xs" spacing={4} withPadding>
        {caveats.map((caveat, index) => (
          <List.Item key={`${index}-${caveat.slice(0, 24)}`}>{caveat}</List.Item>
        ))}
      </List>
    </Alert>
  );
};
