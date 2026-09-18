import React from 'react';
import { Badge, Box, Button, Checkbox, Divider, Group, Paper, Stack, Text, Title, Tooltip } from '@mantine/core';
import {
  IconAlertTriangle,
  IconClock,
  IconFileSearch,
  IconShieldCheck,
  IconSparkles,
} from '@tabler/icons-react';

import type { AccessibilitySettings, ReadingBlock, ThemePalette } from '../types';
import { formatBionic } from '../utils/bionic';
import { MicroQuizCard } from './MicroQuizCard';

interface Props {
  block: ReadingBlock;
  settings: AccessibilitySettings;
  palette: ThemePalette;
  anchorVerified: boolean;
  isActive: boolean;
  isRead: boolean;
  onInspectSource: (block: ReadingBlock) => void;
  onQuizAnswered: (blockId: number, correct: boolean) => void;
  onToggleRead: (blockId: number) => void;
}

export const ReadingBlockCard: React.FC<Props> = ({
  block,
  settings,
  palette,
  anchorVerified,
  isActive,
  isRead,
  onInspectSource,
  onQuizAnswered,
  onToggleRead,
}) => (
  <Paper
    id={`cognita-block-${block.block_id}`}
    shadow="xs"
    radius="md"
    p="xl"
    mb="xl"
    withBorder
    className={isActive ? 'cognita-block-active' : undefined}
    style={{
      backgroundColor: palette.surface,
      borderColor: palette.border,
      lineHeight: settings.lineHeight,
      fontSize: `${settings.fontSize}px`,
      letterSpacing: `${settings.letterSpacing}em`,
      opacity: isRead ? 0.86 : 1,
      scrollMarginTop: 90,
    }}
  >
    {/* Block header ------------------------------------------------- */}
    <Group justify="space-between" mb="md" align="flex-start" wrap="wrap">
      <Group gap="xs" wrap="nowrap" align="center">
        <Badge size="lg" color="indigo" variant="light">
          Block {block.block_id}
        </Badge>
        <Title order={3} size="h4" style={{ letterSpacing: 'inherit' }}>
          {block.headline}
        </Title>
      </Group>

      <Group gap="xs" wrap="nowrap">
        <Tooltip label="Focus sprint length calibrated at 130 words per minute">
          <Badge
            leftSection={<IconClock size={13} />}
            color="gray"
            variant="outline"
            style={{ cursor: 'help' }}
          >
            {block.estimated_reading_seconds}s sprint
          </Badge>
        </Tooltip>
        <Checkbox
          size="sm"
          checked={isRead}
          onChange={() => onToggleRead(block.block_id)}
          label="Read"
          aria-label={`Mark block ${block.block_id} as read`}
          styles={{ label: { fontSize: 12 } }}
        />
      </Group>
    </Group>

    {/* Cognitive chunks --------------------------------------------- */}
    <Stack gap="sm" mb="lg">
      {block.bionic_chunks.map((chunk, index) => (
        <Text
          key={`${block.block_id}-chunk-${index}`}
          component="p"
          m={0}
          style={{
            fontSize: 'inherit',
            lineHeight: 'inherit',
            letterSpacing: 'inherit',
            textWrap: 'pretty',
          }}
        >
          {settings.bionicMode ? formatBionic(chunk) : chunk}
        </Text>
      ))}
    </Stack>

    {/* Key takeaway -------------------------------------------------- */}
    <Box
      p="sm"
      mb="md"
      style={{ backgroundColor: palette.shortcutBackground, borderRadius: 8 }}
    >
      <Group align="flex-start" gap="xs" wrap="nowrap">
        <IconSparkles size={17} color={palette.accent} style={{ marginTop: 3 }} aria-hidden />
        <Text size="sm" fw={600} style={{ flex: 1 }}>
          Core takeaway: {block.key_takeaway}
        </Text>
      </Group>
    </Box>

    {/* Provenance action -------------------------------------------- */}
    <Group justify="space-between" align="center" wrap="wrap">
      <Group gap={6} wrap="nowrap">
        {anchorVerified ? (
          <>
            <IconShieldCheck size={15} color="#2B8A3E" aria-hidden />
            <Text size="xs" c={palette.mutedText}>
              Citation anchor verified verbatim against your source text
            </Text>
          </>
        ) : (
          <>
            <IconAlertTriangle size={15} color="#E8590C" aria-hidden />
            <Text size="xs" c="#E8590C">
              Anchor could not be matched verbatim — treat this block as unverified
            </Text>
          </>
        )}
      </Group>

      <Button
        variant="subtle"
        size="xs"
        color="gray"
        leftSection={<IconFileSearch size={14} />}
        onClick={() => onInspectSource(block)}
      >
        Verify in original source
      </Button>
    </Group>

    {/* Checkpoint quiz ----------------------------------------------- */}
    {block.quiz && (
      <>
        <Divider my="lg" />
        <MicroQuizCard
          quiz={block.quiz}
          palette={palette}
          onAnswered={(correct) => onQuizAnswered(block.block_id, correct)}
        />
      </>
    )}
  </Paper>
);
