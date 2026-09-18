import React from 'react';
import { ActionIcon, Badge, Box, Button, Group, Progress, Text, Tooltip } from '@mantine/core';
import { IconAccessible, IconArrowBackUp, IconBrain } from '@tabler/icons-react';

import type { ThemePalette } from '../types';

interface Props {
  hasData: boolean;
  progress: number;
  palette: ThemePalette;
  onOpenSettings: () => void;
  onReset: () => void;
}

export const Header: React.FC<Props> = ({
  hasData,
  progress,
  palette,
  onOpenSettings,
  onReset,
}) => (
  <Box
    h="100%"
    px={{ base: 'sm', md: 'lg' }}
    style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}
  >
    <Group gap={8} wrap="nowrap" style={{ flexShrink: 0 }}>
      <IconBrain size={26} color={palette.accent} aria-hidden />
      <Box>
        <Text fw={700} size="lg" lh={1.1} style={{ letterSpacing: '-0.01em' }}>
          Cognita
        </Text>
        <Text size="xs" c="dimmed" lh={1.2} visibleFrom="sm">
          Cognitive accessibility engine
        </Text>
      </Box>
    </Group>

    <Tooltip label="UN Sustainable Development Goal 10: Reduced Inequalities — Target 10.2 / 10.3">
      <Badge
        color="indigo"
        variant="light"
        size="sm"
        visibleFrom="sm"
        style={{ flexShrink: 0, cursor: 'help' }}
      >
        SDG 10 · Reduced Inequalities
      </Badge>
    </Tooltip>

    {hasData && (
      <Group gap="xs" style={{ flex: 1, minWidth: 80 }} wrap="nowrap">
        <Progress
          value={progress}
          size="sm"
          radius="xl"
          color="teal"
          style={{ flex: 1 }}
          aria-label={`Reading progress: ${Math.round(progress)} percent`}
        />
        <Text size="xs" c="dimmed" style={{ whiteSpace: 'nowrap' }} visibleFrom="md">
          {Math.round(progress)}% read
        </Text>
      </Group>
    )}

    <Group gap="xs" ml="auto" wrap="nowrap" style={{ flexShrink: 0 }}>
      {hasData && (
        <Button
          variant="subtle"
          size="xs"
          color="gray"
          leftSection={<IconArrowBackUp size={15} />}
          onClick={onReset}
        >
          New text
        </Button>
      )}
      <Tooltip label="Accessibility settings">
        <ActionIcon
          variant="light"
          size="lg"
          color="indigo"
          onClick={onOpenSettings}
          aria-label="Open accessibility settings"
        >
          <IconAccessible size={20} />
        </ActionIcon>
      </Tooltip>
    </Group>
  </Box>
);
